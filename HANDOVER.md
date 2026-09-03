# us_report_daily — 프로젝트 인수인계 문서 (v3)

---

## 1. 업무 목적

매일 아침, INFOMAX 엑셀 파일(`us_data.xlsx`)에서 시장 지표를 자동으로 읽어
T0 / 전일대비 / 전월대비 / YTD 를 계산한 뒤, 디자인된 HTML 레포트를 생성한다.
위원 발언 · 시황 · 경제지표 · 주간 일정은 사용자가 CLI로 입력한다.
생성된 HTML은 브라우저에서 열면 모든 텍스트를 직접 수정할 수 있고,
"사본 저장" 버튼으로 수정 내용이 포함된 정적 HTML 파일을 내보낼 수 있다.

---

## 2. 파이참 프로젝트 파일 구조

```
us_report_daily/                ← 프로젝트 루트 (PyCharm 프로젝트)
│
├── run.py                      ← ★ 매일 실행하는 진입점
├── requirements.txt            ← openpyxl 만 필요
├── us_data.xlsx                ← INFOMAX 엑셀 파일 (매일 업데이트됨)
│
├── content/
│   └── content.json            ← 수기입력 저장소 (자동 생성)
│
├── output/
│   └── report_YYYYMMDD.html    ← 생성된 레포트 (자동 생성)
│
├── templates/
│   └── template.html           ← HTML 레포트 템플릿
│
└── src/
    └── us_report_daily/
        ├── __init__.py
        ├── config.py           ← ★ 파일 경로 설정 (경로 변경 시 여기만 수정)
        ├── mapping.py          ← 항목명 → 엑셀 시트/열 위치 매핑
        ├── excel_extract.py    ← openpyxl로 엑셀 읽기
        ├── dates.py            ← 기준일/전일/전월/연초 날짜 계산
        ├── calc.py             ← T0/1D/1M/YTD 수치 계산
        ├── content_store.py    ← content.json 로드/저장/초기화
        ├── cli.py              ← 수기입력 대화형 CLI
        ├── report_generator.py ← 엑셀 읽기 → 플레이스홀더 딕셔너리 생성
        └── template_renderer.py← 딕셔너리 + content.json → 완성 HTML
```

---

## 3. 파일 경로 변경 방법 (★ 중요)

`src/us_report_daily/config.py` 파일 **하나**만 수정하면 됨:

```python
# config.py
XLSX_PATH     = os.path.join(_ROOT, "us_data.xlsx")       # 엑셀 파일명
TEMPLATE_PATH = os.path.join(_ROOT, "templates", "template.html")
CONTENT_PATH  = os.path.join(_ROOT, "content", "content.json")
OUTPUT_DIR    = os.path.join(_ROOT, "output")
```

예: 엑셀 파일을 `data/` 폴더로 옮기면 → `os.path.join(_ROOT, "data", "us_data.xlsx")`

---

## 4. 매일 실행 순서

```bash
python run.py
```
1. 기준일 입력 (YYYYMMDD, 기본값 오늘)
2. 전영업일 갭 입력 (평일=0, 월요일=2, 공휴일=1)
3. 수기입력 여부 → Y
4. 초기화 여부 → Y → content.json 전체 초기화
5. 수기입력 메뉴 (위원발언 / 시황 / 지표 / 일정)
6. 레포트 자동 생성 → output/report_YYYYMMDD.html
7. 브라우저에서 열어 미세 수정 → 사본 저장

---

## 5. HTML 레이아웃

```
[편집 툴바]  사본저장 / 위원추가 / 지표국가 / 지표행     ← sticky
──────────────────────────────────────────────────────
 HEADER: Fixed Income Daily
──────────────────────┬───────────────────────────────
 좌: 한국 & 외환       │  우: 증시 & 채권 & 원자재
  ┌ KR BOND 카테고리  │  ┌ EQUITY 카테고리
  │ 통안2Y / 국고3Y   │  │ KOSPI / NIKKEI / 상해 / DOW / S&P / NASDAQ
  │ 국고5Y / 국고10Y  │  ├ US TREASURY 카테고리
  │ 국채3년선물        │  │ T-Note2yr / T-Note10yr / T-Bill30yr
  ├ FX 카테고리        │  ├ INTL BOND (10Y) 카테고리
  │ USD/KRW / NDF     │  │ 독일10Y / 영국10Y / 일본10Y
  │ DXY / JPY / EUR   │  └ COMMODITY & RATES 카테고리
  │ JPY/KRW / CNY     │    WTI / GOLD / SOFR / TED spread
  └ GBP/USD           │
──────────────────────┴───────────────────────────────
 경제지표 (국가 고정 컬럼)  │  위원 발언 (추가/삭제 O)
──────────────────────────────────────────────────────
 경제지표 시황 (전체폭 텍스트)
──────────────────────────────────────────────────────
 Summary 2×2  채권 | 증시 / 유가 | 환시
──────────────────────────────────────────────────────
 주간 일정 달력 (월~금 5열)
```

**카테고리 구분**: 각 카테고리 시작 전에 `.cat-sep` 행 (연초록 배경, DM Mono uppercase 텍스트)

**경제지표 국가 컬럼**: 별도 행 없이 `rowspan`으로 고정 — 국가가 좌측에 세로로 병합되어 표시

---

## 6. 엑셀 열 위치 매핑 (mapping.py)

### 국내채권 시트 (BondSpec: date/prev/today 3컬럼)
| 항목 | date_col | prev_col | today_col |
|---|---|---|---|
| 통안 2Y | 10 | 11 | 12 |
| 국고 3Y | 1 | 2 | 3 |
| 국고 5Y | 4 | 5 | 6 |
| 국고 10Y | 7 | 8 | 9 |
| 국채3년선물 | 16 | — | 17 |

### 환율 시트
| 항목 | date_col | value_col |
|---|---|---|
| USD/KRW | 10 | 13 (현재가) |
| NDF | 19 | 20 (NDF_MID_Close) |
| Dollar Index | 1 | 3 (KR_MID_Close) |
| USD/JPY | 4 | 6 (Close) |
| EUR/USD | 7 | 9 (Close) |
| JPY/KRW | 16 | 18 (Close) |
| USD/CNY | 24 | 25 |
| GBP/USD | 28 | 29 (Close) |

### 주가지수 시트
| 항목 | date_col | value_col |
|---|---|---|
| KOSPI | 1 | 2 |
| NIKKEI | 5 | 7 |
| DOW | 9 | 11 |
| NASDAQ | 13 | 15 |
| S&P500 | 17 | 19 |

### 해외채권 시트 (블록당 5컬럼: 일자/시가/현재가/전일대비/등락률)
| 항목 | date_col | value_col(현재가) |
|---|---|---|
| T-Note 2yr | 1 | 3 |
| T-Note 10yr | 6 | 8 |
| T-Bill 30yr | 11 | 13 |
| **독일 10Y** | **16** | **18** |
| **영국 10Y** | **21** | **23** |
| **일본 10Y** | **26** | **28** |

### 기타
| 항목 | 시트 | date_col | value_col |
|---|---|---|---|
| 중국상해종합 | 지수 | 1 | 2 |
| SOFR | 외환 | 5 | 6 |
| TED spread | 지수 | 27 | 28 |
| WTI | 원자재 | 1 | 3 |
| GOLD | 원자재 | 10 | 11 |

---

## 7. 계산 방식

```
T0  = asof 날짜 이전 가장 최근 값
1D  = T0 - 전영업일 값  [금리bp차 / 나머지 등락률%]
1M  = T0 - 30일 전 가장 가까운 영업일 값
YTD = T0 - 해당 연도 1/2 기준 첫 영업일 값
```

국내채권(BondSpec): "당일" 컬럼 = T0, "산출일" 컬럼 = 전일 기준

---

## 8. content.json 구조

```json
{
  "speakers": [{"name":"이름","org":"소속","text":"발언내용"}],
  "summary":  {"채권":"","증시":"","유가":"","환시":""},
  "지표시황":  "경제지표 전반 코멘트",
  "indicators": [
    {"region":"🇺🇸 US","items":[
      {"name":"지표명","actual":"값","survey":"예상","prior":"이전"}
    ]}
  ],
  "schedule": {
    "MON":[{"country":"US","event":"이벤트","highlight":false}],
    "TUE":[], "WED":[], "THU":[], "FRI":[]
  },
  "schedule_labels": {"MON":"2/17","TUE":"2/18","WED":"2/19","THU":"2/20","FRI":"2/21"}
}
```

---

## 9. 플레이스홀더 규칙

```
{{통안 2Y|T0}}         → 숫자값 ("3.14")
{{CLS|통안 2Y|1D}}     → CSS class (p/n/fl/v)
{{SPEAKERS_HTML}}       → 위원발언 HTML
{{INDICATORS_HTML}}     → 경제지표 테이블 tbody (rowspan 구조)
{{SCHEDULE_HTML}}       → 달력 5열 HTML
{{SUM_채권}} 등         → 시황 텍스트
{{지표시황}}            → 지표시황 텍스트
{{REPORT_DATE}}         → "2026. 02. 19"
{{REPORT_WEEKDAY}}      → "수요일"
```

---

## 10. 디자인 토큰

```css
--green:     #1B4332   /* 헤더, 섹션 타이틀 배경 */
--green-mid: #2D6A4F   /* 테이블 헤더 */
--green-lt:  #EBF4EF   /* 카테고리 구분행, 달력 날짜, 국가 컬럼 배경 */
--gold:      #E8B84B   /* 강조, 헤더 하단선, 버튼 */
--pos:       #145230   /* 양수 초록 */
--neg:       #8B1A1A   /* 음수 빨강 */
폰트: Noto Sans KR + DM Mono + Playfair Display
페이지폭: 794px (A4)
```

---

## 11. 개발 간략 로그

### 완료
- openpyxl 기반 엑셀 읽기 (xlwings 없음)
- 열 위치 기반 매핑 (블록이름 탐색 없음)
- **독일/영국/일본 10Y 추가** (해외채권 시트 col 16/21/26)
- **config.py 단일 경로 관리** (파일 이동 시 1줄만 수정)
- **카테고리 구분행** (KR BOND / FX / EQUITY / US TREASURY / INTL BOND / COMMODITY)
- **경제지표 국가 고정 컬럼** (rowspan, 별도 헤더 행 없음)
- **위원 추가/삭제 버튼** (JS, id="speakers-body")
- 경제지표 국가/행 추가/삭제
- 경제지표 시황 섹션 (전체폭)
- 모든 텍스트 contenteditable
- 사본 저장 (수정 내용 포함 HTML 다운로드)
- 매일 초기화 질문
