"""
Health Canada Record of Non-Significant Change document builder (Python).
"""
from doc_common import (
    init_document, add_paragraph, add_bullet, add_bullet_bold,
    add_h1, add_h2, add_spacer,
    add_info_table, add_before_after_table,
    add_cover_page, add_revision_history, add_toc, add_footer,
)


def build_hc_document(product_info: dict, change_info: dict,
                      assessment: dict, metadata: dict):
    """Health Canada 비중대 변경 기록 문서 생성"""
    doc_number = metadata.get("docNumber", "[NSC-HC-XXXX-YYYY]")
    doc = init_document()
    add_footer(doc, doc_number)

    add_cover_page(
        doc,
        doc_title="RECORD OF NON-SIGNIFICANT CHANGE",
        doc_subtitle=f"Health Canada – Medical Device Licence\n{change_info['changeTitle']}",
        doc_number=doc_number,
        rev_no=metadata.get("revisionNo", "00"),
        effective_date=metadata.get("effectiveDate", "[YYYY-MM-DD]"),
        prepared_by=metadata.get("preparedBy", ""),
        reviewed_by=metadata.get("reviewedBy", ""),
        approved_by=metadata.get("approvedBy", ""),
    )

    add_revision_history(doc, metadata)
    add_toc(doc)

    # ===== Body =====
    add_h1(doc, "1. Purpose")
    add_paragraph(
        doc,
        'This document records the evaluation of a change to the licensed device under '
        'Section 34 of the Medical Devices Regulations (CMDR) and the Health Canada Guidance '
        'Document: "Guidance on the Interpretation of Significant Change of a Medical Device – '
        'Types of Changes," and confirms that the change is not a significant change. Therefore, '
        'an amendment to the Medical Device Licence is not required prior to implementation.'
    )

    add_h1(doc, "2. Device & Licence Information")
    add_info_table(doc, [
        ("Model Name",                   product_info.get("modelName", "[Model Name]")),
        ("Device Class (CMDR)",          product_info.get("deviceClass", "[Class]")),
        ("Medical Device Licence No.",   product_info.get("hcLicenceNo", "N/A")),
        ("Licence Holder",               product_info.get("manufacturer", "[Manufacturer]")),
        ("Manufacturer Address",         product_info.get("manufacturerAddress", "[Address]")),
    ])

    add_h1(doc, "3. Description of the Change")
    add_before_after_table(doc, [
        [f"{change_info['componentName']} – Item",
         change_info.get("beforeValue", ""),
         change_info.get("afterValue", "")],
    ])
    add_spacer(doc)
    add_paragraph(doc, f"Reason: {change_info.get('reason', '[Reason for change]')}")
    add_paragraph(doc, f"Description: {change_info.get('description', '[Description]')}")

    add_h1(doc, "4. Significance Assessment per Health Canada Guidance")
    add_paragraph(
        doc,
        'The change has been evaluated against each category described in the Health Canada '
        'Guidance "Types of Changes":'
    )
    add_spacer(doc)

    add_h2(doc, "Decision Path")
    for q in assessment["path"]:
        if q["answer"] is None:
            continue
        answer_text = "Yes" if q["answer"] else "No"
        add_bullet_bold(doc, f"{q['id']}. ", f"{q['text']} — {answer_text}.")

    add_h1(doc, "5. Conclusion")
    add_paragraph(doc, assessment["summary"])

    add_h1(doc, "6. References")
    add_bullet(doc, "Health Canada Guidance Document: Guidance on the Interpretation of Significant Change of a Medical Device – Types of Changes")
    add_bullet(doc, "Medical Devices Regulations (CMDR), Sections 34–35")
    add_bullet(doc, "ISO 13485 – Medical devices – Quality management systems")
    add_bullet(doc, f"Original Medical Device Licence No. {product_info.get('hcLicenceNo', 'N/A')}")
    add_bullet(doc, "Component manufacturer Letter / Certificate of Equivalence dated [YYYY-MM-DD]")

    return doc
