"""Presentation helpers: CSS and small HTML builders.

Everything that originates from the model or the uploaded document is escaped
before it is placed into HTML.
"""

from html import escape

RISK_LABEL = {"High": "High", "Medium": "Medium", "Low": "Low", "None": "Compliant", "Review": "Review"}
RISK_DOT = {"High": "🔴", "Medium": "🟠", "Low": "🟡", "None": "🟢", "Review": "⚪"}

CSS = """
<style>
[data-testid="stMainBlockContainer"] { padding-top: 2.2rem; max-width: 1180px; }
[data-testid="stSidebar"] { border-right: 1px solid #e3e8ef; }

.nda-header { background: linear-gradient(120deg, #16293f 0%, #1f3a5f 60%, #2c5282 100%);
  color: #fff; border-radius: 14px; padding: 26px 32px; margin-bottom: 14px;
  display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; flex-wrap: wrap; }
.nda-header h1 { font-family: "Source Serif 4", "Source Serif Pro", Georgia, serif; color: #fff; font-size: 2rem; margin: 2px 0 6px 0; padding: 0; line-height: 1.15; }
.nda-header p { color: #d5deea; margin: 0; font-size: 0.98rem; max-width: 620px; }
.nda-eyebrow { text-transform: uppercase; letter-spacing: 0.14em; font-size: 0.72rem; color: #9fb6d1; font-weight: 600; }
.nda-pill { background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.25);
  border-radius: 999px; padding: 6px 14px; font-size: 0.8rem; color: #eaf0f7; white-space: nowrap; }

.nda-notice { background: #fff8eb; border: 1px solid #f3dcae; border-left: 4px solid #d9911a;
  border-radius: 8px; padding: 10px 16px; font-size: 0.9rem; color: #5c4210; margin-bottom: 6px; }

.nda-steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-top: 18px; }
.nda-step { background: #f4f6f9; border: 1px solid #e3e8ef; border-radius: 12px; padding: 18px 20px; }
.nda-step .num { display: inline-flex; width: 28px; height: 28px; border-radius: 50%; background: #1f3a5f;
  color: #fff; align-items: center; justify-content: center; font-weight: 700; font-size: 0.85rem; margin-bottom: 8px; }
.nda-step h4 { margin: 0 0 4px 0; padding: 0; font-size: 1.02rem; color: #1c2433; }
.nda-step p { margin: 0; font-size: 0.9rem; color: #55617a; }

.nda-doc { display: flex; align-items: baseline; gap: 12px; flex-wrap: wrap; margin: 14px 0 2px 0; }
.nda-doc .name { font-size: 1.25rem; font-weight: 700; color: #1c2433; }
.nda-doc .meta { font-size: 0.85rem; color: #6b7690; }

.nda-summary { background: #f4f6f9; border-radius: 12px; padding: 16px 20px; margin: 6px 0 14px 0; font-size: 0.95rem; }
.nda-summary .label { text-transform: uppercase; letter-spacing: 0.1em; font-size: 0.7rem; color: #6b7690; font-weight: 700; }
.nda-summary p { margin: 2px 0 10px 0; }
.nda-summary p:last-child { margin-bottom: 0; }

.nda-metrics { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 16px; }
.nda-metric { border: 1px solid #e3e8ef; border-top: 4px solid #cbd5e1; border-radius: 10px; padding: 12px 16px; background: #fff; }
.nda-metric .value { font-size: 1.9rem; font-weight: 700; line-height: 1.1; color: #1c2433; }
.nda-metric .label { font-size: 0.82rem; color: #6b7690; }
.nda-metric.high { border-top-color: #dc2626; } .nda-metric.medium { border-top-color: #ea8a0c; }
.nda-metric.low { border-top-color: #e3c21c; } .nda-metric.none { border-top-color: #16a34a; }

.nda-table-wrap { border: 1px solid #e3e8ef; border-radius: 12px; overflow-x: auto; margin-bottom: 8px; }
table.nda-table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
.nda-table th { background: #1f3a5f; color: #fff; text-align: left; padding: 10px 14px; font-weight: 600;
  font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.06em; white-space: nowrap; }
.nda-table td { padding: 12px 14px; border-top: 1px solid #e9edf3; vertical-align: top; color: #1c2433; }
.nda-table tr:nth-child(even) td { background: #fafbfd; }
.nda-table td.topic { font-weight: 600; min-width: 170px; }
.nda-table td.nowrap { white-space: nowrap; }

.badge { display: inline-block; padding: 2px 11px; border-radius: 999px; font-size: 0.78rem; font-weight: 700; white-space: nowrap; }
.badge-high { background: #fde8e8; color: #9b1c1c; } .badge-medium { background: #fdebd0; color: #8a4b08; }
.badge-low { background: #fdf6c3; color: #6f5600; } .badge-none { background: #dcfce7; color: #166534; }
.badge-review { background: #e5e7eb; color: #374151; }
.check-ok { color: #166534; font-weight: 600; font-size: 0.82rem; white-space: nowrap; }
.check-bad { color: #9b1c1c; font-weight: 700; font-size: 0.82rem; }
.check-na { color: #94a0b8; font-size: 0.82rem; }

.nda-field { text-transform: uppercase; letter-spacing: 0.1em; font-size: 0.7rem; color: #6b7690; font-weight: 700; margin: 4px 0 2px 0; }
.nda-text { font-size: 0.94rem; margin: 0 0 8px 0; }
.nda-quote { border-left: 4px solid #1f3a5f; background: #f4f6f9; border-radius: 0 8px 8px 0;
  padding: 10px 16px; font-family: Georgia, 'Times New Roman', serif; font-size: 0.95rem; color: #27334a; margin: 0 0 8px 0; }
@media (max-width: 800px) { .nda-steps, .nda-metrics { grid-template-columns: 1fr 1fr; } }
</style>
"""


def _slug(risk: str) -> str:
    return risk.lower() if risk in RISK_LABEL else "review"


def badge(risk: str) -> str:
    return f'<span class="badge badge-{_slug(risk)}">{escape(RISK_LABEL.get(risk, risk))}</span>'


def quote_check(value: str) -> str:
    if value == "Verified":
        return '<span class="check-ok">✓ Verified</span>'
    if value == "Not found in document":
        return '<span class="check-bad">✗ Not found in document</span>'
    return '<span class="check-na">n/a</span>'


def header(firm: str, version: str) -> str:
    return (
        '<div class="nda-header"><div>'
        '<div class="nda-eyebrow">Legal innovation</div>'
        "<h1>NDA Review Assistant</h1>"
        "<p>A first-pass review of an NDA against the firm playbook, with quoted clauses, "
        "risk ratings, fallback wording and Q&amp;A.</p></div>"
        f'<div class="nda-pill">{escape(firm)} · Playbook v{escape(str(version))}</div></div>'
    )


def notice(disclaimer: str) -> str:
    return f'<div class="nda-notice">{escape(disclaimer)}</div>'


def steps() -> str:
    items = [
        ("Upload", "Add an NDA as a PDF or DOCX in the sidebar, or load one of the sample documents."),
        ("Review", "Each playbook topic is rated, with the clause quoted and fallback wording proposed."),
        ("Ask and export", "Ask follow-up questions about the NDA and export the findings to CSV or Word."),
    ]
    cards = "".join(f'<div class="nda-step"><div class="num">{i}</div><h4>{t}</h4><p>{d}</p></div>'
                    for i, (t, d) in enumerate(items, 1))
    return f'<div class="nda-steps">{cards}</div>'


def doc_title(name: str, n_chars: int) -> str:
    words = f"{n_chars:,} characters extracted"
    return f'<div class="nda-doc"><span class="name">{escape(name)}</span><span class="meta">{words}</span></div>'


def summary(parties: str, text: str) -> str:
    return ('<div class="nda-summary"><div class="label">Parties</div>'
            f"<p>{escape(parties)}</p><div class=\"label\">Summary</div><p>{escape(text)}</p></div>")


def metrics(rows: list[dict]) -> str:
    cards = ""
    for level, label in [("High", "High risk"), ("Medium", "Medium risk"), ("Low", "Low risk"), ("None", "Compliant")]:
        n = sum(1 for r in rows if r["Risk"] == level)
        cards += (f'<div class="nda-metric {level.lower()}"><div class="value">{n}</div>'
                  f'<div class="label">{label}</div></div>')
    return f'<div class="nda-metrics">{cards}</div>'


def findings_table(rows: list[dict]) -> str:
    head = "".join(f"<th>{h}</th>" for h in ["Topic", "Status", "Risk", "Clause", "Issue", "Quote check"])
    body = ""
    for r in rows:
        body += (
            f'<tr><td class="topic">{escape(r["Topic"])}</td>'
            f'<td class="nowrap">{escape(r["Status"])}</td>'
            f"<td>{badge(r['Risk'])}</td>"
            f'<td class="nowrap">{escape(r["Clause"])}</td>'
            f"<td>{escape(r['Issue'])}</td>"
            f"<td>{quote_check(r['Quote check'])}</td></tr>"
        )
    return (f'<div class="nda-table-wrap"><table class="nda-table"><thead><tr>{head}</tr></thead>'
            f"<tbody>{body}</tbody></table></div>")


def finding_detail(row: dict) -> str:
    html = (f'<div class="nda-field">Assessment &nbsp;{badge(row["Risk"])}</div>'
            f'<p class="nda-text">{escape(row["Issue"])}</p>')
    if row["Quoted clause"]:
        clause = f"Clause {escape(row['Clause'])}" if row["Clause"] else "Clause"
        html += (f'<div class="nda-field">{clause} &nbsp;{quote_check(row["Quote check"])}</div>'
                 f'<div class="nda-quote">{escape(row["Quoted clause"])}</div>')
    if row["Suggested fallback wording"]:
        html += '<div class="nda-field">Suggested fallback wording</div>'
    return html


def md_safe(text: str) -> str:
    """Stop Streamlit treating dollar amounts in legal text as LaTeX."""
    return text.replace("$", "\\$")
