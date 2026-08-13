"""
Health Canada Assessor
Reference: Guidance on the Interpretation of Significant Change of a
           Medical Device – Types of Changes

Per CMDR Section 34, a significant change is one that could affect:
    (a) Manufacturing process, facility, or equipment
    (b) Manufacturing quality control procedures
    (c) Design of the device, including its performance specifications,
        materials, energy source, software, or accessories
    (d) Intended use of the device
"""


def run_hc_questionnaire(ask, ask_yes_no, change_info: dict) -> dict:
    print("  ── HC Type (a): Manufacturing Process / Facility / Equipment ──")
    a1 = ask_yes_no("    a1. 제조 공정 변경이 있습니까?")
    a2 = ask_yes_no("    a2. 제조 시설(facility) 변경이 있습니까?")
    a3 = ask_yes_no("    a3. 주요 제조 장비(equipment) 변경이 있습니까?")

    print("\n  ── HC Type (b): Manufacturing Quality Control ──")
    b1 = ask_yes_no("    b1. QC 절차 또는 시험 방법 변경이 있습니까?")
    b2 = ask_yes_no("    b2. 합격 기준(acceptance criteria) 변경이 있습니까?")

    print("\n  ── HC Type (c): Design / Performance / Material / Energy / Software ──")
    c1 = ask_yes_no("    c1. 설계 변경이 있습니까? (단순 명칭 변경은 제외)")
    c2 = ask_yes_no("    c2. 성능 사양(performance specification) 변경이 있습니까?")
    c3 = ask_yes_no("    c3. 환자 접촉 재료 변경이 있습니까?")
    c4 = ask_yes_no("    c4. 에너지원(energy source) 변경이 있습니까?")
    c5 = ask_yes_no("    c5. 소프트웨어 변경이 있습니까? (사이버보안 패치 등 minor 제외)")
    c6 = ask_yes_no("    c6. 액세서리 추가/변경이 있습니까?")

    print("\n  ── HC Type (d): Intended Use ──")
    d1 = ask_yes_no("    d1. 사용 목적(intended use) 확장 또는 변경이 있습니까?")
    d2 = ask_yes_no("    d2. 금기사항(contraindication) 추가/삭제가 있습니까?")
    d3 = ask_yes_no("    d3. 환자군(patient population) 변경이 있습니까?")
    d4 = ask_yes_no("    d4. 사용 기간(period of use) 변경이 있습니까?")

    return {
        "a1": a1, "a2": a2, "a3": a3,
        "b1": b1, "b2": b2,
        "c1": c1, "c2": c2, "c3": c3, "c4": c4, "c5": c5, "c6": c6,
        "d1": d1, "d2": d2, "d3": d3, "d4": d4
    }


def assess_hc(answers: dict, change_info: dict) -> dict:
    a = answers

    type_a = {
        "name": "(a) Manufacturing Process / Facility / Equipment",
        "items": [
            {"text": "Manufacturing process change", "significant": a.get("a1", False)},
            {"text": "Manufacturing facility change", "significant": a.get("a2", False)},
            {"text": "Manufacturing equipment change", "significant": a.get("a3", False)},
        ],
        "significant": any([a.get("a1"), a.get("a2"), a.get("a3")]),
    }

    type_b = {
        "name": "(b) Manufacturing Quality Control Procedures",
        "items": [
            {"text": "QC procedure / test method change", "significant": a.get("b1", False)},
            {"text": "Acceptance criteria change", "significant": a.get("b2", False)},
        ],
        "significant": any([a.get("b1"), a.get("b2")]),
    }

    type_c = {
        "name": "(c) Design / Performance / Materials / Energy / Software / Accessories",
        "items": [
            {"text": "Design change (excluding nomenclature)", "significant": a.get("c1", False)},
            {"text": "Performance specification change", "significant": a.get("c2", False)},
            {"text": "Patient-contacting material change", "significant": a.get("c3", False)},
            {"text": "Energy source change", "significant": a.get("c4", False)},
            {"text": "Software change (excluding minor)", "significant": a.get("c5", False)},
            {"text": "Accessory addition/change", "significant": a.get("c6", False)},
        ],
        "significant": any([a.get("c1"), a.get("c2"), a.get("c3"), a.get("c4"), a.get("c5"), a.get("c6")]),
    }

    type_d = {
        "name": "(d) Intended Use",
        "items": [
            {"text": "Intended use extension/change", "significant": a.get("d1", False)},
            {"text": "Contraindication add/remove", "significant": a.get("d2", False)},
            {"text": "Patient population change", "significant": a.get("d3", False)},
            {"text": "Period of use change", "significant": a.get("d4", False)},
        ],
        "significant": any([a.get("d1"), a.get("d2"), a.get("d3"), a.get("d4")]),
    }

    is_significant = type_a["significant"] or type_b["significant"] or type_c["significant"] or type_d["significant"]

    return {
        "country": "HC",
        "guidance": "Health Canada Guidance Document: Guidance on the Interpretation of Significant Change of a Medical Device – Types of Changes",
        "isSignificant": is_significant,
        "requiredAction": "Licence Amendment Application required" if is_significant else "Internal record only; no Licence Amendment",
        "types": [type_a, type_b, type_c, type_d],
        "summary": (
            "The change is classified as a significant change under CMDR Section 34. A Licence Amendment application must be submitted to Health Canada prior to implementation."
            if is_significant else
            "The change does not meet any of the criteria for a significant change under CMDR Section 34. The change may be implemented under the manufacturer's ISO 13485 / MDSAP-certified QMS, with records available to Health Canada upon request."
        ),
    }
