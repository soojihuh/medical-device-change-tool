"""
EU MDR Non-Significant Change Assessment document builder (Python).
Per MDCG 2020-3.
"""
from doc_common import (
    init_document, add_paragraph, add_bullet, add_bullet_bold,
    add_h1, add_h2, add_spacer,
    add_info_table, add_before_after_table,
    add_cover_page, add_revision_history, add_toc, add_footer,
)


def build_eu_document(product_info: dict, change_info: dict,
                      assessment: dict, metadata: dict):
    """EU MDR 비중대 변경 평가 문서 생성"""
    doc_number = metadata.get("docNumber", "[NSC-EU-XXXX-YYYY]")
    doc = init_document()
    add_footer(doc, doc_number)

    add_cover_page(
        doc,
        doc_title="NON-SIGNIFICANT CHANGE ASSESSMENT",
        doc_subtitle=f"EU MDR (Regulation (EU) 2017/745) – per MDCG 2020-3\n{change_info['changeTitle']}",
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
    add_h1(doc, "1. Purpose & Scope")
    add_paragraph(
        doc,
        'This document evaluates a proposed change to the device under the requirements of '
        'Regulation (EU) 2017/745 (MDR) and the guidance MDCG 2020-3 Rev.1 "Guidance on '
        'significant changes regarding the transitional provision under Article 120 of the MDR." '
        'The assessment determines whether the change qualifies as a significant change in design '
        'or intended purpose, which would require prior notification to and approval by the '
        'Notified Body.'
    )
    add_paragraph(
        doc,
        'Note: The decision charts in MDCG 2020-3 are used here as a structured methodology '
        'consistent with industry practice and aligned with the Notified Body change-notification '
        'procedures applicable under the MDR certificate.'
    )

    add_h1(doc, "2. Device & Certificate Information")
    add_info_table(doc, [
        ("Model Name",                  product_info.get("modelName", "[Model Name]")),
        ("Risk Class (MDR Annex VIII)", product_info.get("deviceClass", "[Class]")),
        ("Basic UDI-DI",                product_info.get("euBasicUDIDI", "N/A")),
        ("Legal Manufacturer",          product_info.get("manufacturer", "[Manufacturer]")),
        ("Manufacturer Address",        product_info.get("manufacturerAddress", "[Address]")),
        ("Notified Body",               product_info.get("euNotifiedBody", "N/A")),
        ("Certificate Number",          product_info.get("euCertNumber", "N/A")),
    ])

    add_h1(doc, "3. Description of the Change")
    add_before_after_table(doc, [
        [f"{change_info['componentName']} – Item",
         change_info.get("beforeValue", ""),
         change_info.get("afterValue", "")],
    ])
    add_spacer(doc)
    add_paragraph(doc, f"Reason: {change_info.get('reason', '[Reason]')}")
    add_paragraph(doc, f"Description: {change_info.get('description', '[Description]')}")

    add_h1(doc, "4. Assessment per MDCG 2020-3 Decision Charts")

    if assessment.get("nbDetectorException"):
        add_paragraph(
            doc,
            "NB Exception Note: The Notified Body has confirmed that detector additions or changes "
            "are classified as non-significant changes and do not require prior NB approval. "
            "The MDCG 2020-3 decision charts are completed below for documentation purposes only.",
            bold=True,
        )
        add_spacer(doc)

    for chart in assessment["charts"]:
        add_h2(doc, chart["name"])
        if not chart["applicable"]:
            add_paragraph(doc, "Not applicable to this device.")
            continue
        if not chart["questions"]:
            add_paragraph(doc, "Not applicable.")
            continue
        for q in chart["questions"]:
            answer_text = "Yes" if q["answer"] else "No"
            add_bullet_bold(doc, f"{q['id']}. ", f"{q['text']} — {answer_text}.")
        outcome = "Significant." if chart["significant"] else "Not significant."
        add_paragraph(doc, f"Outcome: {outcome}", bold=True)

    add_h1(doc, "5. Conclusion of MDCG 2020-3 Assessment")
    add_paragraph(doc, assessment["summary"])

    add_h1(doc, "6. Technical Documentation Updates (MDR Annex II / III)")
    add_bullet(doc, "Annex II – Section 1 (Device Description and Specification): Updated where applicable.")
    add_bullet(doc, "Annex II – BOM and component list: Updated.")
    add_bullet(doc, "Annex II – Labelling and IFU: Updated where the changed item is referenced.")
    add_bullet(doc, "Declaration of Conformity (Annex IV): Re-evaluation of need for re-issue based on impact to device identification, intended purpose, or applied harmonised standards.")
    add_bullet(doc, "UDI: Re-evaluation of need for new UDI-DI based on whether design or manufacturer changed.")
    add_bullet(doc, "EUDAMED: Update of device registration data as required.")

    add_h1(doc, "7. References")
    add_bullet(doc, "Regulation (EU) 2017/745 (MDR), in particular Article 10, Article 15, Annex II, Annex III, Annex IX")
    add_bullet(doc, "MDCG 2020-3 Rev.1 – Guidance on significant changes regarding the transitional provision under Article 120 of the MDR")
    add_bullet(doc, "ISO 13485 – Medical devices – Quality management systems")
    add_bullet(doc, f"Notified Body Certificate No. {product_info.get('euCertNumber', 'N/A')}")
    add_bullet(doc, "Component manufacturer Letter / Certificate of Equivalence dated [YYYY-MM-DD]")

    return doc
