"""
FDA Assessor
Reference: Deciding When to Submit a 510(k) for a Change to an Existing Device (Oct 2017)

Decision logic:
    - Flowchart A: Labeling changes
    - Flowchart B: Technology / Engineering / Performance changes
    - Flowchart C: Materials changes

    If any flowchart concludes that the change "could significantly affect"
    safety / effectiveness → New 510(k) required (Significant)
    Otherwise → Letter to File (Not Significant)
"""


def run_fda_questionnaire(ask, ask_yes_no, change_info: dict) -> dict:
    print("  ── Flowchart A: Labeling Changes ──")
    A1 = ask_yes_no("    A1. 의도된 용도(Indications for Use) 변경이 있습니까?")
    A2 = ask_yes_no("    A2. 금기사항(Contraindication) 추가/수정이 있습니까?")
    A3 = ask_yes_no("    A3. 경고/주의/이상반응 표기에 새로운 정보가 추가됩니까?")
    A4 = ask_yes_no("    A4. 라벨 변경이 임상적 기능/성능에 영향을 줄 수 있습니까?")

    print("\n  ── Flowchart B: Technology / Engineering / Performance ──")
    B1 = ask_yes_no("    B1. 작동 원리(Operating Principle) 변경이 있습니까?")
    B2 = ask_yes_no("    B2. 에너지 유형(Energy Type) 변경이 있습니까?")
    B3 = ask_yes_no("    B3. 환경 사양(Environmental Spec) 변경이 있습니까?")
    B4 = ask_yes_no("    B4. 사용 인터페이스(Use of Device) 변경이 있습니까?")
    B5 = ask_yes_no("    B5. 설계 / 구성품 / 사양 변경이 있습니까? (단순 명칭 변경은 제외)")
    B6 = ask_yes_no("    B6. 멸균/포장/유효기간 변경이 있습니까?")
    B7 = ask_yes_no("    B7. 변경이 성능 사양에 중대한 영향을 미칠 수 있습니까?")

    print("\n  ── Flowchart C: Materials ──")
    C1 = ask_yes_no("    C1. 환자/사용자와 접촉하는 재료가 변경되었습니까?")
    C2 = ask_yes_no("    C2. 재료 변경이 생체적합성에 영향을 줄 수 있습니까?")

    return {
        "A1": A1, "A2": A2, "A3": A3, "A4": A4,
        "B1": B1, "B2": B2, "B3": B3, "B4": B4, "B5": B5, "B6": B6, "B7": B7,
        "C1": C1, "C2": C2
    }


def assess_fda(answers: dict, change_info: dict) -> dict:
    a = answers

    flowchart_a = {
        "name": "Flowchart A – Labeling Changes",
        "questions": [
            {"id": "A1", "text": "Change to indications for use?", "answer": a.get("A1", False), "significant": a.get("A1", False)},
            {"id": "A2", "text": "Add/modify a contraindication?", "answer": a.get("A2", False), "significant": a.get("A2", False)},
            {"id": "A3", "text": "New warnings/precautions/adverse events?", "answer": a.get("A3", False), "significant": a.get("A3", False)},
            {"id": "A4", "text": "Could the change significantly affect clinical functionality/performance?", "answer": a.get("A4", False), "significant": a.get("A4", False)},
        ],
        "significant": any([a.get("A1"), a.get("A2"), a.get("A3"), a.get("A4")]),
    }

    flowchart_b = {
        "name": "Flowchart B – Technology, Engineering, and Performance Changes",
        "questions": [
            {"id": "B1", "text": "Change in operating principle?", "answer": a.get("B1", False), "significant": a.get("B1", False)},
            {"id": "B2", "text": "Change in energy type?", "answer": a.get("B2", False), "significant": a.get("B2", False)},
            {"id": "B3", "text": "Change in environmental specifications?", "answer": a.get("B3", False), "significant": a.get("B3", False)},
            {"id": "B4", "text": "Change in use of the device?", "answer": a.get("B4", False), "significant": a.get("B4", False)},
            {"id": "B5", "text": "Change in design/components/specification (excluding nomenclature)?", "answer": a.get("B5", False), "significant": a.get("B5", False)},
            {"id": "B6", "text": "Change in sterilization, packaging, expiration dating?", "answer": a.get("B6", False), "significant": a.get("B6", False)},
            {"id": "B7", "text": "Could the change significantly affect performance specifications?", "answer": a.get("B7", False), "significant": a.get("B7", False)},
        ],
        "significant": any([a.get("B1"), a.get("B2"), a.get("B3"), a.get("B4"), a.get("B5"), a.get("B6"), a.get("B7")]),
    }

    flowchart_c = {
        "name": "Flowchart C – Materials Changes",
        "questions": [
            {"id": "C1", "text": "Change in patient/user contacting material?", "answer": a.get("C1", False), "significant": a.get("C1", False)},
            {"id": "C2", "text": "Could the change affect biocompatibility?", "answer": a.get("C2", False), "significant": a.get("C2", False)},
        ],
        "significant": any([a.get("C1"), a.get("C2")]),
    }

    is_significant = flowchart_a["significant"] or flowchart_b["significant"] or flowchart_c["significant"]

    return {
        "country": "FDA",
        "guidance": "FDA Guidance: Deciding When to Submit a 510(k) for a Change to an Existing Device (October 25, 2017)",
        "isSignificant": is_significant,
        "requiredAction": "New 510(k) submission required" if is_significant else "Letter to File (no new 510(k))",
        "flowcharts": [flowchart_a, flowchart_b, flowchart_c],
        "summary": (
            "The change could significantly affect safety or effectiveness. A new 510(k) submission is required."
            if is_significant else
            "The change does not significantly affect safety or effectiveness, nor is it a major change to intended use. Documentation in a Letter to File is sufficient."
        ),
    }
