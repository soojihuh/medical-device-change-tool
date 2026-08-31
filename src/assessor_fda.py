"""
FDA Assessor
Reference: Deciding When to Submit a 510(k) for a Change to an Existing Device (Oct 25, 2017)

이 모듈은 가이던스의 실제 플로우차트(Main Flowchart, Flowchart A/B/C)를
있는 그대로 의사결정 트리(FDA_GRAPH)로 구현한다. "어느 한 질문이라도 Yes면
중대한 변경"이 아니라, 각 질문의 답에 따라 정해진 다음 질문/결론으로 분기한다.

Flowchart D (In Vitro Diagnostic Devices 전용)는 이 도구에서 지원하지 않는다.
B1/C1에서 IVD로 답하면 "MANUAL_REVIEW_IVD"로 분기하여 수동 검토가 필요함을 표시한다.
"""

TERMINALS = ("NEW_510K", "DOCUMENTATION", "MANUAL_REVIEW_IVD")

# ===== Main Flowchart (Figure 1) =====
FDA_MAIN_ITEMS = [
    {
        "key": "MAIN1",
        "text": "변경이 안전성 또는 유효성을 유의미하게 향상시키려는 의도로 이루어졌습니까? "
                "(예: 임상 결과를 유의미하게 개선, 알려진 위험 완화, 이상반응 대응 등)",
    },
    {"key": "MAIN2", "text": "라벨링(Labeling) 변경입니까?"},
    {"key": "MAIN3", "text": "기술/엔지니어링/성능(Technology, Engineering, or Performance) 변경입니까?"},
    {"key": "MAIN4", "text": "재료(Materials) 변경입니까?"},
]

# ===== Flowchart A: Labeling / B: Technology, Engineering, Performance /
#       C: Materials — combined into one graph so C5 can redirect into B5 =====
FDA_GRAPH = {
    # --- Flowchart A: Labeling Changes ---
    "A1": {"text": "사용목적(Indications for Use) 문구에 변경이 있습니까?", "yes": "A1.1", "no": "A2"},
    "A2": {"text": "금기사항(Contraindication)을 추가하거나 삭제합니까?", "yes": "NEW_510K", "no": "A3"},
    "A3": {"text": "경고(Warning) 또는 주의사항(Precaution)에 변경이 있습니까?", "yes": "A1.1", "no": "A4"},
    "A4": {"text": "사용설명서(Directions for Use)에 영향을 줄 수 있는 변경입니까?", "yes": "A1.1", "no": "DOCUMENTATION"},
    "A1.1": {"text": "단회용(single use only) 라벨을 재사용(reusable) 라벨로 변경합니까?", "yes": "NEW_510K", "no": "A1.2"},
    "A1.2": {"text": "처방(Rx) 전용에서 일반의약품(OTC) 사용으로 변경합니까?", "yes": "NEW_510K", "no": "A1.3"},
    "A1.3": {"text": "기기명 변경이거나, 가독성/명확성 개선만을 위한 변경입니까?", "yes": "DOCUMENTATION", "no": "A1.4"},
    "A1.4": {
        "text": "진단·치료·예방·완화 대상이 되는 새로운 질병, 상태, 또는 환자군을 기술합니까?",
        "yes": "NEW_510K", "no": "A1.5",
    },
    "A1.5": {
        "text": "위험기반평가(risk-based assessment) 결과 새로운 위험 또는 유의미하게 변경된 기존 위험이 확인됩니까?",
        "yes": "NEW_510K", "no": "DOCUMENTATION",
    },

    # --- Flowchart B: Technology, Engineering, and Performance Changes ---
    "B1": {"text": "이 기기는 체외진단기기(IVD, In Vitro Diagnostic Device)입니까?", "yes": "MANUAL_REVIEW_IVD", "no": "B2"},
    "B2": {
        "text": "제어기전(control mechanism), 작동원리(operating principle), 또는 에너지 유형(energy type) 변경입니까?",
        "yes": "NEW_510K", "no": "B3",
    },
    "B3": {"text": "멸균(sterilization), 세척(cleaning), 또는 소독(disinfection) 방법에 변경이 있습니까?", "yes": "B3.1", "no": "B4"},
    "B3.1": {
        "text": "\"Category B\" 또는 신규(novel) 멸균법으로 변경되거나, 무균성 보증수준(SAL)이 낮아지거나, "
                "기기 제공 방식(멸균/비멸균, 단일환자·단일사용/다중사용/다중환자)이 변경됩니까?",
        "yes": "NEW_510K", "no": "B3.2",
    },
    "B3.2": {"text": "변경이 성능 또는 생체적합성(biocompatibility)에 유의미한 영향을 줄 수 있습니까?", "yes": "NEW_510K", "no": "DOCUMENTATION"},
    "B4": {"text": "포장(packaging) 또는 유효기간(expiration dating)에 변경이 있습니까?", "yes": "B4.1", "no": "B5"},
    "B4.1": {
        "text": "기존에 승인된 510(k)에 기술된 것과 동일한 방법/프로토콜을 사용해 이 변경을 뒷받침합니까?",
        "yes": "DOCUMENTATION", "no": "NEW_510K",
    },
    "B5": {
        "text": "그 외 다른 설계 변경(치수, 성능 사양, 무선통신, 구성품/액세서리, 사용자 인터페이스 등)입니까?",
        "yes": "B5.1", "no": "DOCUMENTATION",
    },
    "B5.1": {"text": "변경이 기기의 사용(use)에 유의미한 영향을 줍니까?", "yes": "NEW_510K", "no": "B5.2"},
    "B5.2": {
        "text": "위험기반평가 결과 새로운 위험 또는 유의미하게 변경된 기존 위험이 확인됩니까?",
        "yes": "NEW_510K", "no": "B5.3",
    },
    "B5.3": {"text": "설계 유효성 검증(design validation)을 위해 임상 데이터(clinical data)가 필요합니까?", "yes": "NEW_510K", "no": "B5.4"},
    "B5.4": {
        "text": "설계 검증/유효성평가(V&V) 활동에서 예상치 못한 안전성·유효성 문제가 발견됐습니까?",
        "yes": "NEW_510K", "no": "DOCUMENTATION",
    },

    # --- Flowchart C: Materials Changes ---
    "C1": {"text": "이 기기는 체외진단기기(IVD)입니까?", "yes": "MANUAL_REVIEW_IVD", "no": "C2"},
    "C2": {
        "text": "재료 종류(material type), 배합(formulation), 화학적 조성, 또는 가공(processing) 방법에 변경이 있습니까?",
        "yes": "C3", "no": "DOCUMENTATION",
    },
    "C3": {"text": "변경된 재료가 신체 조직 또는 체액에 직접 또는 간접적으로 접촉합니까?", "yes": "C4", "no": "C5"},
    "C4": {
        "text": "위험평가 결과 새롭거나 증가된 생체적합성(biocompatibility) 우려가 확인됩니까?",
        "yes": "C4.1", "no": "C5",
    },
    "C4.1": {
        "text": "동일한 재료(배합·가공·접촉 유형 및 기간이 같거나 더 위험한 조건)를 이미 유사한 합법 유통 제품에 사용한 이력이 있습니까?",
        "yes": "C5", "no": "NEW_510K",
    },
    "C5": {"text": "이 변경이 기기의 성능 사양(performance specifications)에 영향을 줄 수 있습니까?", "yes": "B5", "no": "DOCUMENTATION"},
}

CHART_ENTRY = {"MAIN2": ("A1", "Flowchart A: Labeling Changes"),
               "MAIN3": ("B1", "Flowchart B: Technology, Engineering, and Performance Changes"),
               "MAIN4": ("C1", "Flowchart C: Materials Changes")}


def walk_fda_graph(start_id: str, answers: dict):
    """
    answers: {node_id: True/False/None}. Walks FDA_GRAPH from start_id following
    the recorded answers until a terminal is reached or an unanswered node is hit.
    Returns (path, outcome) where outcome is None if the walk is incomplete.
    """
    path = []
    node_id = start_id
    while node_id not in TERMINALS:
        node = FDA_GRAPH[node_id]
        ans = answers.get(node_id)
        path.append({"id": node_id, "text": node["text"], "answer": ans})
        if ans is None:
            return path, None
        node_id = node["yes"] if ans else node["no"]
    return path, node_id


def run_fda_questionnaire(ask, ask_yes_no, change_info: dict) -> dict:
    answers = {}

    print("  ── Main Flowchart ──")
    answers["MAIN1"] = ask_yes_no(f"    MAIN1. {FDA_MAIN_ITEMS[0]['text']}")
    if answers["MAIN1"]:
        return answers

    answers["MAIN2"] = ask_yes_no(f"    MAIN2. {FDA_MAIN_ITEMS[1]['text']}")
    answers["MAIN3"] = ask_yes_no(f"    MAIN3. {FDA_MAIN_ITEMS[2]['text']}")
    answers["MAIN4"] = ask_yes_no(f"    MAIN4. {FDA_MAIN_ITEMS[3]['text']}")

    def walk_interactive(start_id):
        node_id = start_id
        while node_id not in TERMINALS:
            node = FDA_GRAPH[node_id]
            ans = ask_yes_no(f"    {node_id}. {node['text']}")
            answers[node_id] = ans
            node_id = node["yes"] if ans else node["no"]

    for main_key, (entry_node, chart_name) in CHART_ENTRY.items():
        if answers.get(main_key):
            print(f"\n  ── {chart_name} ──")
            walk_interactive(entry_node)

    return answers


def assess_fda(answers: dict, change_info: dict) -> dict:
    a = answers
    guidance = "FDA Guidance: Deciding When to Submit a 510(k) for a Change to an Existing Device (October 25, 2017)"

    if a.get("MAIN1") is True:
        return {
            "country": "FDA",
            "guidance": guidance,
            "isSignificant": True,
            "manualReviewRequired": False,
            "requiredAction": "New 510(k) submission required",
            "path": [{"id": "MAIN1", "text": FDA_MAIN_ITEMS[0]["text"], "answer": True}],
            "summary": (
                "변경이 안전성 또는 유효성을 유의미하게 향상시키려는 의도로 이루어진 것으로 확인되어, "
                "21 CFR 807.81(a)(3)에 따라 다른 고려사항과 무관하게 신규 510(k) 제출이 필요합니다."
            ),
        }

    path = [{"id": "MAIN1", "text": FDA_MAIN_ITEMS[0]["text"], "answer": a.get("MAIN1")}]
    for item in FDA_MAIN_ITEMS[1:]:
        path.append({"id": item["key"], "text": item["text"], "answer": a.get(item["key"])})

    significant = False
    manual_review = False
    any_chart_invoked = False

    for main_key, (entry_node, _chart_name) in CHART_ENTRY.items():
        if a.get(main_key):
            any_chart_invoked = True
            chart_path, outcome = walk_fda_graph(entry_node, a)
            path += chart_path
            if outcome == "NEW_510K":
                significant = True
            elif outcome == "MANUAL_REVIEW_IVD":
                manual_review = True

    if manual_review:
        significant = True
        required_action = "IVD 전용 평가(Flowchart D) 필요 — 본 도구는 지원하지 않으므로 수동 검토 필요"
        summary = (
            "이 변경은 체외진단기기(IVD) 관련 항목으로 식별되어, 본 도구가 지원하지 않는 "
            "Flowchart D(IVD 전용) 평가가 필요합니다. 규제 담당자의 수동 검토가 필요합니다."
        )
    elif significant:
        required_action = "New 510(k) submission required"
        summary = (
            "위험기반평가 결과 이 변경이 기기의 안전성 또는 유효성에 유의미한 영향을 줄 수 있는 것으로 "
            "판단되어, 21 CFR 807.81(a)(3)에 따라 신규 510(k) 제출이 필요합니다."
        )
    elif not any_chart_invoked:
        required_action = "Letter to File (no new 510(k))"
        summary = (
            "이 변경은 라벨링, 기술/엔지니어링/성능, 재료 중 어느 항목에도 해당하지 않는 것으로 확인되어, "
            "Letter to File 문서화로 충분합니다."
        )
    else:
        required_action = "Letter to File (no new 510(k))"
        summary = (
            "해당 플로우차트(들)를 따라 평가한 결과 이 변경은 안전성 또는 유효성에 유의미한 영향을 주지 않는 것으로 "
            "판단되어, 21 CFR 807.81(a)(3) 기준 중대한 변경에 해당하지 않습니다. Letter to File 문서화로 충분합니다."
        )

    return {
        "country": "FDA",
        "guidance": guidance,
        "isSignificant": significant,
        "manualReviewRequired": manual_review,
        "requiredAction": required_action,
        "path": path,
        "summary": summary,
    }
