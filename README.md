# NDA Review Assistant

Playbook-driven first-pass review of non-disclosure agreements. Upload an NDA, get a risk-rated comparison against the firm's agreed positions with the clause quoted and fallback wording ready to paste into a mark-up, then export the findings or ask follow-up questions about the document.

**Live app:** https://nda-review-assistant.streamlit.app/

## Why it exists

NDAs are high volume and low margin. Most of the review is a comparison against positions the firm has already agreed, yet each one takes a fee earner 20 to 40 minutes, and the quality of a first pass varies with who does it and how busy they are. The firm's positions usually sit in a Word playbook that people apply from memory.

NDA Review Assistant does the mechanical comparison in under a minute and leaves the judgement with the lawyer. Every finding shows the clause it relies on, so the reviewer checks the tool's work instead of starting from a blank page.

## What it does

- **Playbook review.** Assesses the NDA against six topics: term, definition of confidential information, exclusions, governing law and jurisdiction, liability and remedies, and non-solicitation.
- **Risk rating.** Rates each topic High, Medium or Low using the thresholds written in the playbook, or marks it Compliant.
- **Quoted clauses.** Quotes the clause relied on, with its clause number, and verifies the quote word for word against the document.
- **Fallback wording.** Proposes replacement wording from the playbook, adapted to the NDA's own defined terms and clause numbering.
- **Export.** Downloads the findings as CSV or as a Word report for the matter file.
- **Q&A.** Answers questions about the uploaded NDA, citing clause numbers and saying plainly when the document is silent.
- **Transparency.** Shows the extracted text, so the reviewer can see exactly what was analysed.

## Using it

1. Upload an NDA as a PDF or DOCX in the sidebar. Two test NDAs are included if you want to see it working first.
2. Click **Run playbook review**. Results appear in under a minute.
3. Read the summary and the findings table, then open each finding for the quoted clause and the fallback wording. High and Medium findings open by default.
4. Export to CSV or Word.
5. Use the **Ask about this NDA** tab for follow-up questions.

### Reading the results

| Rating | Meaning | Action |
|---|---|---|
| High | Outside the firm's acceptable range | Do not sign without partner approval |
| Medium | Departs from the preferred position | Negotiate using the fallback wording |
| Low | Minor departure | Accept if commercially necessary and note on file |
| Compliant | Meets the preferred position | None |
| Review | The tool could not produce a consistent rating | Review the topic manually |

The **Quote check** column shows whether the quoted clause was found word for word in the document. A quote marked "Not found in document" must be checked against the original before it is relied on.

## The playbook

The firm's positions live in one file, [playbook/nda_playbook.yaml](playbook/nda_playbook.yaml). It ships with a balanced UK commercial playbook for mutual NDAs under the name Sample LLP. Replace the firm name and positions with your own.

Each topic has a preferred position, an acceptable position, the triggers for each risk level, and fallback wording. Changes take effect on the next review and need no code changes. Adding a topic means adding one more entry to the file. The playbook version is shown in the app header and should be increased whenever positions change.

## How it works

| Layer | Choice | Why |
|---|---|---|
| Interface | Streamlit | One Python codebase, quick to change in response to user feedback |
| Model | Anthropic Claude API (`claude-opus-5-5` by default) | Strong reasoning over long documents, native structured outputs |
| Structured output | Pydantic schema passed to `messages.parse` | The findings table is built from validated fields, never from parsed free text |
| Playbook | YAML file | Owned and edited by lawyers and knowledge teams, not developers |
| Extraction | `pypdf`, `python-docx` | Covers text-based PDF and DOCX, the formats NDAs arrive in |

The playbook is held in a cached system prompt, which reduces cost and latency for repeat reviews and chat turns.

```
app.py                      Streamlit interface
nda_assistant/extract.py    PDF and DOCX text extraction
nda_assistant/review.py     Prompts, output schema, model calls, safeguards
nda_assistant/export.py     CSV and Word export
nda_assistant/ui.py         Styling and HTML components
playbook/nda_playbook.yaml  The firm playbook
samples/                    Test NDAs (one DOCX, one PDF)
```

## Safeguards

Language models make mistakes. The following controls are built in, and each one is enforced by code, not left to the model.

| Risk | Control |
|---|---|
| Invented or paraphrased clauses | Every quote is checked word for word against the extracted text. A mismatch is flagged in the table and in a warning banner. |
| Incomplete or inconsistent output | Output is schema-constrained. The code guarantees one row per playbook topic. A skipped topic is shown as "Not assessed", and a deviation with no rating is escalated to "Review". |
| The model applying its own view of the law | The model is instructed to apply the playbook thresholds only, and to say so where the playbook does not clearly cover a point. |
| Instructions hidden inside an uploaded document | The NDA is passed as delimited data. The model is told to treat it as text to analyse and to report anything that reads like an instruction. |
| Unreadable files | Scanned and password-protected PDFs are rejected with a clear message. Over-long documents are rejected, never silently truncated. |
| Over-reliance | Each finding shows its clause and reasoning, compliant topics are shown alongside deviations, and a review notice appears on every screen and in every export. |

Supervision and responsibility for the advice stay with the reviewing lawyer.

## Data handling

- The app does not store uploaded documents, findings or chat history. They are held in the browser session and are gone when it ends.
- Document text is sent to the Anthropic API for analysis. Retention and residency are governed by the API agreement on the key in use. For client documents, use a key covered by terms that meet the firm's confidentiality and data protection requirements, and check client terms and outside counsel guidelines on AI use.
- Access can be restricted with an access code (`APP_PASSWORD`). Without it, anyone with the link can use the app.
- The API key is read from the environment or from the host's secret store and is never written to the repository.

## Installation

Requires Python 3.11 or later and an Anthropic API key from [console.anthropic.com](https://console.anthropic.com).

1. Create and activate a virtual environment (PowerShell):

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   On macOS or Linux, activate with `source .venv/bin/activate`. With `uv`, use `uv venv --python 3.12`.

2. Install the dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Create the `.env` file and add the key:

   ```powershell
   Copy-Item .env.example .env
   ```

   Edit `.env` so it reads `ANTHROPIC_API_KEY=sk-ant-...`. The file is excluded from git and must never be committed.

4. Start the app:

   ```powershell
   streamlit run app.py
   ```

5. Open http://localhost:8501.

### Configuration

| Setting | Required | Purpose |
|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | API key used for reviews and Q&A |
| `APP_PASSWORD` | Recommended | Access code users must enter before using the app |
| `NDA_MODEL` | No | Model override. Default is `claude-opus-5-5`. Re-test the ratings before changing it. |

Uploads are limited to 10 MB in [.streamlit/config.toml](.streamlit/config.toml), which also holds the colour theme.

## Deployment

The app deploys to Streamlit Community Cloud from GitHub.

1. Create an empty repository on GitHub (no README), for example `nda-review-assistant`.

2. Push the project:

   ```powershell
   git init
   git add .
   git commit -m "NDA Review Assistant"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/nda-review-assistant.git
   git push -u origin main
   ```

   Run `git status` before committing and confirm `.env` is not listed.

3. Go to [share.streamlit.io](https://share.streamlit.io), sign in with GitHub and choose **Create app**.

4. Select the repository, branch `main` and main file `app.py`. Under **Advanced settings** choose Python 3.12 and add the secrets:

   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   APP_PASSWORD = "choose-an-access-code"
   ```

5. Click **Deploy**. The app is live at a `https://...streamlit.app` address within a couple of minutes. Every push to `main` redeploys it.

Set a monthly spend limit on the API key in the Anthropic console.

## Operating it

- **Playbook ownership.** Name one lawyer as owner of `nda_playbook.yaml`. Changes go through version control with sign-off, and the version number is increased each time.
- **Verification after changes.** After any change to the playbook, prompts or model, run both test NDAs and confirm the expected results below before releasing. As usage grows, extend this to a set of past NDAs with lawyer-agreed ratings and track agreement per topic.
- **Feedback.** Collect the cases where the reviewing lawyer disagreed with a rating. They are the best source of playbook and prompt improvements.
- **Model upgrades.** The model is set in one place (`NDA_MODEL`). Re-run the verification set before upgrading.
- **Cost.** A review costs a few pence. Monitor usage in the Anthropic console.
- **Scaling beyond a team.** For firm-wide use, host inside the firm's own environment behind single sign-on, and add an audit log of who reviewed which document with which model and playbook version.

### Verification set

| File | Document | Expected result |
|---|---|---|
| `samples/sample_nda_1_mutual.docx` | Balanced mutual NDA under English law | No High findings. Medium: missing independent development exclusion, 12 month non-solicit. Low: 5 year survival, non-exclusive jurisdiction. Compliant: definition, liability. |
| `samples/sample_nda_2_one_way.pdf` | One-sided NDA under New York law | High on all six topics: perpetual term, one-way definition, no exclusions, New York law and courts, uncapped indemnity with liquidated damages, 3 year non-solicit and non-dealing. |

Both documents produce these results on the current playbook and default model, with every quoted clause verified. Borderline clauses can be rated differently between runs, which is why the clause and reasoning are always shown. The sources are in `samples/source/` and can be rebuilt with `scripts/make_samples.py`.

## Limitations

- Scanned PDFs are not supported (no OCR).
- The review covers the six playbook topics only. Other provisions, such as assignment or return of information, are not rated, although the summary may mention them.
- Findings are produced as a table and report. The tool does not mark up the original document with tracked changes.
- The playbook assumes the firm's client is a party that both discloses and receives information. A different client position needs its own playbook.

## Roadmap

- Tracked-changes mark-up of the uploaded DOCX
- OCR for scanned documents
- Multiple playbooks, selectable by client or by disclosing and receiving position
- Single sign-on and audit logging
- An evaluation suite built from past NDAs with agreed ratings
