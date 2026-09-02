"""
Health Canada change review document builder (Python).
Lean format matching the company's actual "Review of changes to Health Canada" template
(no cover page / TOC / revision history — just the change details and the
review results, in English for submission).
"""
import re

from doc_common import init_document, add_paragraph, add_spacer, add_page_break, add_info_table

HC_GUIDANCE_TITLE = 'Guidance on how to interpret "significant change" of a medical device: Types of changes'

# Section order on the Health Canada guidance page, lettered the way the company's own
# review documents label them (labelling lands on "H" because in-vitro-diagnostic
# materials — not implemented here — occupies "G").
HC_PREFIX_TO_CHART_LETTER = {
    "MFG": "A",
    "QC": "B",
    "D": "C",
    "S": "D",
    "SW": "E",
    "M": "F",
    "L": "H",
}
HC_MAIN_KEY_TO_CHART_LETTER = {
    "G_MFG": "A",
    "G_QC": "B",
    "G_DESIGN": "C",
    "G_STERILE": "D",
    "G_SW": "E",
    "G_MATERIAL": "F",
    "G_LABEL": "H",
}


def _node_prefix(node_id: str) -> str:
    match = re.match(r"^[A-Za-z]+", node_id)
    return match.group(0) if match else node_id


def _qa_line(doc, text_en: str, answer, suffix: str = ""):
    add_paragraph(doc, text_en, after_pt=2)
    arrow = "YES" if answer else "NO"
    add_paragraph(doc, f"→ {arrow}{suffix}", after_pt=10)


def build_hc_document(product_info: dict, change_info: dict,
                      assessment: dict, metadata: dict):
    """Health Canada 변경 검토 문서 생성 (회사 실제 제출 양식)"""
    doc = init_document()

    # ===== Change details =====
    add_paragraph(doc, "Change the Existing device for Health Canada", bold=True)
    add_spacer(doc)

    add_paragraph(doc, "1) Existing device", bold=True)
    add_paragraph(doc, f"- {product_info.get('hcLicenceNo', 'N/A')} ({product_info.get('modelName', '[Model Name]')})")
    add_spacer(doc)

    add_paragraph(doc, "2) Change Details", bold=True)
    add_paragraph(doc, "(1) Existing registration details", bold=True)
    add_paragraph(doc, change_info.get("componentName", ""), bold=True)
    add_info_table(doc, [("Before", change_info.get("beforeValue", ""))])
    add_spacer(doc)

    add_paragraph(doc, "(2) Change request", bold=True)
    add_paragraph(doc, change_info.get("componentName", ""), bold=True)
    add_info_table(doc, [("After", change_info.get("afterValue", ""))])
    add_spacer(doc)
    add_paragraph(doc, change_info.get("description") or change_info.get("changeTitle", ""))
    add_spacer(doc)

    add_paragraph(doc, "(3) Reason for change", bold=True)
    add_paragraph(doc, change_info.get("reason", "[Reason for change]"))

    add_page_break(doc)

    # ===== Assessment results =====
    add_paragraph(
        doc,
        f"The results of reviewing the changes in accordance with {HC_GUIDANCE_TITLE}.",
        bold=True,
    )
    add_spacer(doc)

    add_paragraph(doc, "- Main Flow chart", bold=True)
    for q in assessment["path"]:
        if q["answer"] is None or q["id"] not in HC_MAIN_KEY_TO_CHART_LETTER:
            continue
        suffix = ""
        if q["answer"]:
            suffix = f" (Go to Flowchart {HC_MAIN_KEY_TO_CHART_LETTER[q['id']]})"
        _qa_line(doc, q["text_en"], q["answer"], suffix)

    last_chart_letter = None
    for q in assessment["path"]:
        if q["answer"] is None or q["id"] in HC_MAIN_KEY_TO_CHART_LETTER:
            continue
        chart_letter = HC_PREFIX_TO_CHART_LETTER.get(_node_prefix(q["id"]), "?")
        if chart_letter != last_chart_letter:
            add_spacer(doc)
            add_paragraph(doc, f"- Flowchart {chart_letter}", bold=True)
            last_chart_letter = chart_letter
        _qa_line(doc, f"{q['id']}: {q['text_en']}", q["answer"])

    add_spacer(doc)
    if assessment["isSignificant"]:
        result_label = "Licence Amendment Required"
        conclusion_label = "Significant Change"
    else:
        result_label = "No Amendment Required, Document in Quality Management System"
        conclusion_label = "Documentation"

    add_paragraph(doc, f"Result: {result_label}.")
    add_spacer(doc)
    add_paragraph(doc, f"The change is considered a {conclusion_label}.", bold=True)

    return doc
