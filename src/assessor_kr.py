"""
KR (식약처/MFDS) Assessor
Reference: 의료기기 허가·신고·심사 등에 관한 규정
    - [별표 3] 경미한 변경사항(제19조 관련) — 140개 항목, 10개 분류
    - [별표 4] 변경대상 판단 흐름도(제19조 관련) — 주 흐름도, 흐름도 1(모양 및 구조·원재료),
      흐름도 2(제조방법·사용목적·성능·사용방법·사용시주의사항·사용기간·저장방법·시험규격)

FDA/EU와 달리 국내 기준은 하나로 이어지는 단일 판단 흐름(주 흐름도 → 흐름도1/흐름도2)이라,
별도의 "메인 항목 + 서브차트" 구조 없이 KR_GRAPH 하나를 시작 노드(START)부터 끝까지
그대로 걷는(walk) 방식으로 구현한다. 앱(app.py)의 walk_graph_ui 헬퍼를 그대로 재사용할 수 있다.

[별표 3]의 140개 개별 항목은 나열하지 않고, 그 목록에 해당하는지를 묻는 게이트 질문
(KR_M2_1/F1_1/F2_1 — "제19조제4항제2호에 따른 변경대상인가?")으로 대신한다. 실제 검토 시
[별표 3] 목록을 참고해 답변한다.

주의: "제19조제1항", "제19조제4항제2호", "제19조제6항" 등 조문 번호는 [별표 4] 흐름도에 표기된
그대로이며, 조문 원문은 이 모듈에 포함되어 있지 않다. 조문 원문이 있으면 질문 문구를 더 정확히
다듬을 수 있다.
"""

TERMINALS = (
    "MINOR_IMMEDIATE", "MINOR_ANNUAL",
    "APPROVAL_NO_TECH_REVIEW", "APPROVAL_TECH_REVIEW",
    "APPROVAL_CLINICAL", "NEW_APPLICATION",
)

TERMINAL_LABEL = {
    "MINOR_IMMEDIATE": "경미한 변경 대상 (즉시보고, 제19조제6항)",
    "MINOR_ANNUAL": "경미한 변경 대상 (연차보고)",
    "APPROVAL_NO_TECH_REVIEW": "변경허가·인증 (기술문서심사 불필요)",
    "APPROVAL_TECH_REVIEW": "변경허가·인증 (기술문서심사 필요)",
    "APPROVAL_CLINICAL": "변경허가 (임상자료심사 필요)",
    "NEW_APPLICATION": "신규 허가·인증·신고",
}

# 이 중 "경미한 변경 대상"(즉시/연차보고)만 이 도구가 문서(내부 검토기록)를 생성하는 대상이다.
NON_SIGNIFICANT_TERMINALS = ("MINOR_IMMEDIATE", "MINOR_ANNUAL")

START = "M1"

KR_GRAPH = {
    # ===== 주 흐름도 =====
    "M1": {
        "text": "수출전용 의료기기입니까?",
        "yes": "M1a", "no": "M2",
    },
    "M1a": {
        "text": "사용목적, 제조소 소재지 변경·추가 및 양도·양수를 제외한 변경입니까?",
        "yes": "MINOR_ANNUAL", "no": "APPROVAL_NO_TECH_REVIEW",
    },
    "M2": {
        "text": "포장단위, 제조원, 명칭, 비고, 「의료기기법」 제7조에 따른 허가조건의 변경입니까?",
        "yes": "M2a", "no": "M3",
    },
    "M2a": {
        "text": "이 변경이 [별표 3] 경미한 변경사항(제19조제4항제2호)에 해당하는 항목입니까?",
        "yes": "MINOR_ANNUAL", "no": "APPROVAL_NO_TECH_REVIEW",
    },
    "M3": {
        "text": "[별표 7]에서 정하고 있는 임상자료 제출 대상의 변경입니까?",
        "yes": "APPROVAL_CLINICAL", "no": "M4",
    },
    "M4": {
        "text": "모양 및 구조, 원재료의 변경입니까?",
        "yes": "F1_1", "no": "M5",
    },
    "M5": {
        "text": "제조방법, 사용목적, 성능, 사용방법, 사용 시 주의사항, 저장방법, 사용기간, 시험규격 등의 변경입니까?",
        "yes": "F2_1", "no": "APPROVAL_NO_TECH_REVIEW",
    },

    # ===== 흐름도 1: 모양 및 구조, 원재료 변경 =====
    "F1_1": {
        "text": "이 변경이 [별표 3] 경미한 변경사항(제19조제4항제2호)에 해당하는 항목입니까?",
        "yes": "F1_1a", "no": "F1_2",
    },
    "F1_1a": {
        "text": "제19조제6항에 따른 30일 이내 보고 사항입니까?",
        "yes": "MINOR_IMMEDIATE", "no": "MINOR_ANNUAL",
    },
    "F1_2": {
        "text": "작용원리(operating principle)의 변경입니까?",
        "yes": "F1_2a", "no": "F1_3",
    },
    "F1_2a": {
        "text": "제19조제1항에 따라 기존 제품과 동일하다고 볼 수 없는 신규 허가·인증·신고 대상 변경입니까?",
        "yes": "NEW_APPLICATION", "no": "APPROVAL_TECH_REVIEW",
    },
    "F1_3": {
        "text": "모양 및 구조의 변경입니까?",
        "yes": "F1_3a", "no": "F1_4",
    },
    "F1_3a": {
        "text": "외형/치수(용품) 또는 특성(전기) 변경에 따라 사용목적, 성능 또는 시험규격이 함께 변경됩니까?",
        "yes": "F2_1", "no": "F1_4",
    },
    "F1_4": {
        "text": "[용품] 원재료의 규격 및 분량 변경 또는 [전기] 부분품의 \"규격 또는 특성\"의 변경입니까?",
        "yes": "F1_4a", "no": "F1_5",
    },
    "F1_4a": {
        "text": "동일 제조자(제조의뢰자 포함)의 기허가(인증) 제품과 동일한 구성품(용품) 또는 부분품(전기)으로 변경합니까?",
        "yes": "APPROVAL_NO_TECH_REVIEW", "no": "F1_4b",
    },
    "F1_4b": {
        "text": "변경되는 구성품(또는 부분품)이 기허가(인증) 제품과 접촉부위·접촉시간·제조방법·사용방법·시험규격이 모두 동일합니까?",
        "yes": "APPROVAL_NO_TECH_REVIEW", "no": "APPROVAL_TECH_REVIEW",
    },
    "F1_5": {
        "text": "원재료의 인체접촉여부 및 접촉부위, 첨가목적의 변경입니까?",
        "yes": "APPROVAL_TECH_REVIEW", "no": "F1_6",
    },
    "F1_6": {
        "text": "동물유래 원재료인 경우, 동물의 명칭·원산국·연령·사용부위·처리공정·성분명의 변경입니까?",
        "yes": "APPROVAL_TECH_REVIEW", "no": "APPROVAL_NO_TECH_REVIEW",
    },

    # ===== 흐름도 2: 제조방법·사용목적·성능·사용방법·사용시주의사항·사용기간·저장방법·시험규격의 변경 =====
    "F2_1": {
        "text": "이 변경이 [별표 3] 경미한 변경사항(제19조제4항제2호)에 해당하는 항목입니까?",
        "yes": "F2_1a", "no": "F2_2",
    },
    "F2_1a": {
        "text": "제19조제6항에 따른 30일 이내 보고 사항입니까?",
        "yes": "MINOR_IMMEDIATE", "no": "MINOR_ANNUAL",
    },
    "F2_2": {
        "text": "제조방법의 변경입니까? (멸균방법 변경 포함)",
        "yes": "APPROVAL_TECH_REVIEW", "no": "F2_3",
    },
    "F2_3": {
        "text": "사용목적의 변경입니까?",
        "yes": "APPROVAL_TECH_REVIEW", "no": "F2_4",
    },
    "F2_4": {
        "text": "성능의 변경입니까?",
        "yes": "APPROVAL_TECH_REVIEW", "no": "F2_5",
    },
    "F2_5": {
        "text": "사용방법 및 사용 시 주의사항의 변경입니까? (예: 사용횟수/시간, 멸균주체 변경, 타 기기와의 호환·운용 변경, "
                "사용부위·적응증·사용자 변경, 자기공명 환경 안전성 변경, 금기사항·부작용 등 삭제, 잠재적 합병증 사항 변경)",
        "yes": "APPROVAL_TECH_REVIEW", "no": "F2_6",
    },
    "F2_6": {
        "text": "사용기간의 변경입니까?",
        "yes": "F2_6a", "no": "F2_7",
    },
    "F2_6a": {
        "text": "사용기간을 연장하는 변경입니까?",
        "yes": "APPROVAL_TECH_REVIEW", "no": "F2_7",
    },
    "F2_7": {
        "text": "저장방법(멸균포장방법 등)의 변경입니까?",
        "yes": "APPROVAL_TECH_REVIEW", "no": "F2_8",
    },
    "F2_8": {
        "text": "시험규격의 변경입니까?",
        "yes": "APPROVAL_TECH_REVIEW", "no": "APPROVAL_NO_TECH_REVIEW",
    },
}


def walk_kr_graph(start_id: str, answers: dict):
    """
    answers: {node_id: True/False/None}. KR_GRAPH를 start_id부터 걸으며,
    terminal에 도달하거나 아직 답변되지 않은 노드를 만나면 멈춘다.
    Returns (path, outcome) — outcome은 아직 진행 중이면 None.
    """
    path = []
    node_id = start_id
    while node_id not in TERMINALS:
        node = KR_GRAPH[node_id]
        ans = answers.get(node_id)
        path.append({"id": node_id, "text": node["text"], "answer": ans})
        if ans is None:
            return path, None
        node_id = node["yes"] if ans else node["no"]
    return path, node_id


def assess_kr(answers: dict, change_info: dict) -> dict:
    guidance = (
        "의료기기 허가·신고·심사 등에 관한 규정 [별표 3] 경미한 변경사항 및 "
        "[별표 4] 변경대상 판단 흐름도 (제19조 관련)"
    )

    path, outcome = walk_kr_graph(START, answers)

    if outcome is None:
        # 미완료 상태 — 호출부(app.py)에서 completeness 체크로 걸러지지만 방어적으로 처리
        return {
            "country": "KR",
            "guidance": guidance,
            "isSignificant": True,
            "requiredAction": "평가 진행 중",
            "path": path,
            "summary": "아직 모든 문항에 답변되지 않았습니다.",
        }

    significant = outcome not in NON_SIGNIFICANT_TERMINALS
    required_action = TERMINAL_LABEL[outcome]

    if outcome == "MINOR_IMMEDIATE":
        summary = (
            "[별표 4] 변경대상 판단 흐름도에 따라 이 변경은 경미한 변경사항에 해당하며, "
            "제19조제6항에 따라 변경 후 30일 이내에 식품의약품안전처에 보고해야 합니다."
        )
    elif outcome == "MINOR_ANNUAL":
        summary = (
            "[별표 4] 변경대상 판단 흐름도에 따라 이 변경은 경미한 변경사항에 해당하며, "
            "별도의 변경허가·인증 신청 없이 연차보고 시 함께 보고하면 됩니다."
        )
    elif outcome == "APPROVAL_NO_TECH_REVIEW":
        significant = True
        required_action = TERMINAL_LABEL[outcome]
        summary = (
            "이 변경은 경미한 변경사항에 해당하지 않아 변경허가·인증 신청이 필요하나, "
            "[별표 4] 흐름도상 기술문서심사는 필요하지 않은 것으로 판단됩니다."
        )
    elif outcome == "APPROVAL_TECH_REVIEW":
        summary = (
            "이 변경은 [별표 4] 흐름도상 기술문서심사가 필요한 변경허가·인증 대상으로 판단됩니다."
        )
    elif outcome == "APPROVAL_CLINICAL":
        summary = (
            "이 변경은 [별표 7]에서 정하는 임상자료 제출 대상에 해당하여, "
            "임상자료심사를 포함한 변경허가가 필요합니다."
        )
    else:  # NEW_APPLICATION
        summary = (
            "이 변경은 작용원리 변경 등으로 기존 제품과 동일하다고 볼 수 없어, "
            "변경허가가 아닌 신규 허가·인증·신고 대상으로 판단됩니다."
        )

    return {
        "country": "KR",
        "guidance": guidance,
        "isSignificant": significant,
        "terminal": outcome,
        "requiredAction": required_action,
        "path": path,
        "summary": summary,
    }
