"""NDA Review Assistant: Streamlit front end."""

import hashlib
import hmac
import os
from pathlib import Path

import anthropic
import streamlit as st
from dotenv import load_dotenv

from nda_assistant import ui
from nda_assistant.export import DISCLAIMER, to_csv, to_docx
from nda_assistant.extract import ExtractionError, extract_text
from nda_assistant.review import (ReviewError, build_rows, get_client,
                                  load_playbook, review_nda, stream_answer)

load_dotenv()
SAMPLES_DIR = Path(__file__).parent / "samples"

st.set_page_config(page_title="NDA Review Assistant", page_icon="⚖️", layout="wide")
st.html(ui.CSS)


def get_setting(name: str) -> str | None:
    """Read from the environment (.env locally) or Streamlit secrets (when deployed)."""
    value = os.getenv(name)
    if value:
        return value
    try:
        return st.secrets[name]
    except Exception:
        return None


def api_error_message(exc: Exception) -> str:
    if isinstance(exc, anthropic.AuthenticationError):
        return "The API key was rejected. Check ANTHROPIC_API_KEY."
    if isinstance(exc, anthropic.RateLimitError):
        return "The AI service is busy or the rate limit was reached. Please try again in a minute."
    if isinstance(exc, anthropic.APIConnectionError):
        return "Could not reach the AI service. Check your internet connection and try again."
    if isinstance(exc, anthropic.APIStatusError):
        return f"The AI service returned an error ({exc.status_code}). Please try again."
    return f"Something went wrong: {exc}"


def require_password() -> None:
    """Optional gate for the public demo so the API key is not open to everyone."""
    expected = get_setting("APP_PASSWORD")
    if not expected or st.session_state.get("authed"):
        return
    entered = st.text_input("Access code", type="password")
    if entered:
        if hmac.compare_digest(entered, expected):
            st.session_state.authed = True
            st.rerun()
        st.error("Incorrect access code.")
    st.stop()


def load_document(name: str, data: bytes) -> None:
    """Extract text and reset per-document state when a new file arrives."""
    digest = hashlib.sha256(data).hexdigest()
    if st.session_state.get("doc_hash") == digest:
        return
    try:
        text = extract_text(name, data)
    except ExtractionError as exc:
        st.error(str(exc))
        return
    st.session_state.update(doc_hash=digest, doc_name=name, doc_text=text,
                            review=None, rows=None, chat=[])


# ---------- Page ----------

playbook, playbook_raw = load_playbook()
st.html(ui.header(playbook["firm"], playbook["version"]))
st.html(ui.notice(DISCLAIMER))
require_password()
api_key = get_setting("ANTHROPIC_API_KEY")

with st.sidebar:
    st.subheader("Choose an NDA")
    uploaded = st.file_uploader("Upload a PDF or DOCX", type=["pdf", "docx"])
    if uploaded:
        load_document(uploaded.name, uploaded.getvalue())

    samples = sorted(p for p in SAMPLES_DIR.glob("*") if p.suffix.lower() in (".pdf", ".docx"))
    if samples:
        choice = st.selectbox("Or try a sample", samples, format_func=lambda p: p.name)
        if st.button("Load sample", width="stretch"):
            load_document(choice.name, choice.read_bytes())

    st.divider()
    st.subheader("Playbook positions")
    for topic in playbook["topics"]:
        with st.expander(topic["name"]):
            st.markdown(f"**Preferred:** {topic['preferred']}")
            st.markdown(f"**Acceptable:** {topic['acceptable']}")

if not api_key:
    st.error("No API key found. Add ANTHROPIC_API_KEY to a .env file (local) or to the app "
             "secrets (Streamlit Community Cloud). See the README.")
    st.stop()

if not st.session_state.get("doc_text"):
    st.html(ui.steps())
    st.stop()

client = get_client(api_key)
doc_text = st.session_state.doc_text
st.html(ui.doc_title(st.session_state.doc_name, len(doc_text)))
tab_review, tab_chat, tab_text = st.tabs(["Playbook review", "Ask about this NDA", "Extracted text"])

with tab_review:
    has_review = bool(st.session_state.get("rows"))
    if st.button("Run the review again" if has_review else "Run playbook review",
                 type="secondary" if has_review else "primary"):
        with st.spinner("Reviewing against the playbook. This usually takes under a minute."):
            try:
                review = review_nda(client, doc_text, playbook_raw)
                st.session_state.review = review
                st.session_state.rows = build_rows(review, playbook, doc_text)
                st.rerun()
            except ReviewError as exc:
                st.error(str(exc))
            except anthropic.APIError as exc:
                st.error(api_error_message(exc))

    review, rows = st.session_state.get("review"), st.session_state.get("rows")
    if review and rows:
        if not review.is_nda:
            st.error("This does not look like an NDA. The results below may not be meaningful.")
        st.html(ui.summary(review.parties, review.summary))
        st.html(ui.metrics(rows))

        unverified = sum(1 for r in rows if r["Quote check"] == "Not found in document")
        if unverified:
            st.warning(f"{unverified} quoted clause(s) could not be matched word for word to "
                       "the document. Check them against the original before relying on them.")

        st.html(ui.findings_table(rows))

        stem = Path(st.session_state.doc_name).stem
        c1, c2, _ = st.columns([1, 1, 3])
        c1.download_button("Export CSV", to_csv(rows), f"{stem}_review.csv", "text/csv",
                           width="stretch", icon=":material/download:")
        c2.download_button(
            "Export Word report", to_docx(rows, st.session_state.doc_name, review.parties, review.summary),
            f"{stem}_review.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            width="stretch", icon=":material/description:")

        st.markdown("#### Clause detail and fallback wording")
        for row in rows:
            flagged = row["Risk"] in ("High", "Medium", "Review")
            label = f"{ui.RISK_DOT.get(row['Risk'], '⚪')} {row['Topic']}"
            with st.expander(label, expanded=flagged):
                st.html(ui.finding_detail(row))
                if row["Suggested fallback wording"]:
                    st.code(row["Suggested fallback wording"], language=None, wrap_lines=True)

with tab_chat:
    st.caption("Answers are grounded in the uploaded NDA and the playbook. Verify against the source.")
    chat = st.session_state.setdefault("chat", [])
    box = st.container(height=440)
    if not chat:
        box.caption("No questions yet. Try: Can we share this information with our external advisers?")
    for message in chat:
        box.chat_message(message["role"]).markdown(ui.md_safe(message["content"]))

    if question := st.chat_input("Ask a question about this NDA"):
        chat.append({"role": "user", "content": question})
        box.chat_message("user").markdown(ui.md_safe(question))
        raw_chunks: list[str] = []

        def display_stream():
            for chunk in stream_answer(client, doc_text, playbook_raw, chat):
                raw_chunks.append(chunk)
                yield ui.md_safe(chunk)

        try:
            with box.chat_message("assistant"):
                st.write_stream(display_stream())
            chat.append({"role": "assistant", "content": "".join(raw_chunks)})
        except anthropic.APIError as exc:
            chat.pop()
            st.error(api_error_message(exc))

with tab_text:
    st.caption("This is exactly what the model sees. If the extraction looks wrong, the review will be too.")
    st.text_area("Extracted text", doc_text, height=500, label_visibility="collapsed")
