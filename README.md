# Medical Device Change Assessment & Documentation Tool (Python)

의료기기 변경 사항을 FDA, Health Canada, EU MDR 가이던스에 따라 평가하고, 중대하지 않은 변경에 대해 인허가 문서를 자동 생성하는 도구입니다.

## 평가 기준 가이던스

| 국가 | 가이던스 | 출처 |
|------|----------|------|
| 🇺🇸 FDA | Deciding When to Submit a 510(k) for a Change to an Existing Device (Oct 2017) | https://www.fda.gov/regulatory-information/search-fda-guidance-documents/deciding-when-submit-510k-change-existing-device |
| 🇨🇦 Health Canada | Guidance on the Interpretation of Significant Change of a Medical Device – Types of Changes | https://www.canada.ca/en/health-canada/services/drugs-health-products/medical-devices/application-information/guidance-documents/interpret-significant-change-medical-device/types-changes.html |
| 🇪🇺 EU MDR | MDCG 2020-3 Rev.1 | https://health.ec.europa.eu/medical-devices-sector/new-regulations/guidance-mdcg-endorsed-documents-and-other-guidance_en |

---

## 🚀 빠른 시작 (Windows)

### 1단계: Python 설치 확인

명령 프롬프트(또는 VS Code 터미널)에서:

```cmd
python --version
```

결과:
- `Python 3.x.x` 가 나오면 → 다음 단계로
- 오류가 나면 → https://www.python.org/downloads/ 에서 Python 3.10 이상 설치
  - 설치 시 ⚠️ **"Add Python to PATH" 체크박스 반드시 체크**

### 2단계: 라이브러리 설치

```cmd
pip install -r requirements.txt
```

또는

```cmd
pip install python-docx
```

### 3단계: 실행

```cmd
# 방법 1: 대화형 모드 (질문에 하나씩 답변)
python main.py

# 방법 2: Config 파일로 한 번에 실행 (예시 그대로 실행)
python main.py --config example_config.json

# 방법 3: 테스트 실행 (잘 동작하는지 확인)
python test.py
```

생성된 워드 파일은 `output/` 폴더에 저장됩니다.

---

## 🌐 웹 포털로 실행하기

CLI 대신 브라우저에서 사용할 수 있는 웹 포털(Streamlit) 버전도 있습니다. 로그인 없이 링크만 있으면 누구나 접속할 수 있습니다.

```cmd
# 1. 가상환경 생성 및 패키지 설치 (최초 1회)
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt

# 2. 포털 실행
.venv\Scripts\streamlit run app.py
```

또는 `run_portal.bat`을 더블클릭하면 위 과정을 자동으로 처리합니다.

실행 후 터미널에 표시되는 주소로 접속합니다:
- `http://localhost:8501` — 이 PC에서만 접속 가능
- `http://<사내 IP 또는 PC 이름>:8501` — 같은 사내망의 다른 사람도 접속 가능 (방화벽에서 8501 포트 허용 필요)

평가 로직과 문서 생성 로직은 CLI(`main.py`)와 완전히 동일한 `src/` 모듈을 그대로 사용합니다. 웹 폼에 정보를 입력하고 "평가 실행" → "문서 생성" 버튼을 누르면 워드 파일을 바로 다운로드할 수 있습니다.

### 한→영 번역

"2. 변경 사항 입력"에 한글로 작성한 뒤 **"🌐 한→영 번역"** 버튼을 누르면 Google 번역으로 영문 초안이 생성됩니다. 번역 결과는 그대로 쓰지 말고 검토 후 필요하면 직접 수정하세요. "평가 실행 및 문서 생성에 이 영문 번역본 사용" 체크박스가 켜져 있으면(기본값) 이후 평가/문서 생성에는 이 영문 텍스트가 사용됩니다.

---

## 📁 프로젝트 구조

```
medical_device_change_tool_py/
├── main.py                     # 메인 실행 파일 (대화형 CLI)
├── test.py                     # 단위 테스트
├── example_config.json         # 자동화 실행용 예시 config
├── requirements.txt            # Python 의존성
├── README.md                   # 본 문서
├── run.bat                     # Windows용 원클릭 실행 (선택)
├── src/
│   ├── __init__.py
│   ├── assessor_fda.py         # FDA Flowchart A,B,C 평가 로직
│   ├── assessor_hc.py          # HC Types of Changes (a,b,c,d) 평가 로직
│   ├── assessor_eu.py          # EU MDCG 2020-3 Charts A,B,C,D,E 평가 로직
│   ├── doc_common.py           # 공통 docx 컴포넌트 (표지, TOC, Revision History)
│   ├── doc_fda.py              # FDA Letter to File 문서 생성
│   ├── doc_hc.py               # HC Record of Non-Significant Change 문서 생성
│   └── doc_eu.py               # EU MDR Non-Significant Change Assessment 문서 생성
└── output/                     # 생성된 워드 파일 출력 디렉토리
```

---

## 🔄 워크플로우

```
1. 제품 정보 입력
   ↓
2. 변경 사항 입력
   ↓
3. 국가/지역 선택 (FDA, HC, EU 중 복수 선택 가능)
   ↓
4. 각 국가별 가이던스 질문 응답 → 자동 판정 (Significant / Not Significant)
   ↓
5. Not Significant인 경우만 워드 문서 자동 생성
```

## 평가 로직 요약

### FDA (Flowchart 기반)
- **Flowchart A**: 라벨링 변경 (의도된 용도, 금기, 경고 등)
- **Flowchart B**: 기술/엔지니어링/성능 변경
- **Flowchart C**: 재료 변경
- 어느 하나라도 "Yes" → **신규 510(k) 필요**
- 모두 "No" → **Letter to File** 작성 후 내부 보관

### Health Canada (4가지 Type 기반)
- **(a)** 제조 공정/시설/장비
- **(b)** 제조 QC 절차
- **(c)** 설계/성능/재료/에너지원/소프트웨어/액세서리
- **(d)** 사용 목적
- 어느 하나라도 "Yes" → **License Amendment 필요**
- 모두 "No" → 내부 기록만 유지

### EU MDR (MDCG 2020-3 Charts)
- **Chart A**: 설계/성능 사양
- **Chart B**: 사용 목적
- **Chart C**: 소프트웨어
- **Chart D**: 물질/재료
- **Chart E**: 멸균 (해당 시)
- 어느 하나라도 "Yes" → **Notified Body 사전 승인 필요**
- 모두 "No" → QMS 하에 처리, NB 사전 승인 불필요

---

## 📄 생성되는 문서 구조

각 워드 문서는 다음 구조를 가집니다:

1. **표지** — 문서 제목, 문서 번호, Rev. No., Effective Date, 승인 서명란 (Prepared/Reviewed/Approved)
2. **Revision History** — 개정 이력 표
3. **Table of Contents** — 자동 생성 목차 (Word에서 우클릭 → "필드 업데이트")
4. **본문** — 평가 결과를 반영한 정식 인허가 문서
5. **Footer** — 문서번호 + Page X of Y

---

## 💡 실제 사용 시 권장 워크플로우

신규 변경 사항이 발생했을 때:

1. `example_config.json`을 복사해서 새 파일로 저장 (예: `change_2026_001.json`)
2. 파일을 열어 제품 정보, 변경 내용, 평가 응답을 수정
3. 실행: `python main.py --config change_2026_001.json`
4. `output/` 폴더에서 생성된 워드 파일 확인 → 검토자/승인자 서명 받기

이렇게 하면 모든 변경 평가 기록이 JSON 파일로 남아 나중에 추적도 가능합니다.

---

## ⚠️ 자주 발생하는 문제

| 문제 | 해결 방법 |
|------|----------|
| `'python'은(는) 명령으로 인식되지 않습니다` | Python 미설치 또는 PATH 미등록 → Python 재설치 시 "Add to PATH" 체크 |
| `ModuleNotFoundError: No module named 'docx'` | `pip install python-docx` 실행 |
| `pip` 권한 오류 | `pip install python-docx --user` 사용 |
| 사내 네트워크에서 pip 실패 | 사내 프록시 또는 사내 PyPI 미러 설정 (IT 팀 문의) |
| 한글 입력이 깨짐 | 명령 프롬프트에서 `chcp 65001` 실행 후 다시 |

---

## 🔧 새로운 평가 항목 추가 방법

각 국가별 `src/assessor_*.py` 파일에서 질문지 함수와 평가 함수를 수정하면 됩니다. 평가 결과 객체의 구조는 `doc_*.py`에서 그대로 받아 문서로 렌더링되므로, 새 차트나 항목을 추가하면 문서에도 자동 반영됩니다.

---

## 라이선스

Proprietary – 사내 사용 전용
