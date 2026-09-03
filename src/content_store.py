# src/us_report_daily/content_store.py
import json, os
from config import CONTENT_PATH

EMPTY: dict = {
    "speakers": [],
    "summary": {"채권": "", "증시": "", "유가": "", "환시": ""},
    "지표시황": "",
    "indicators": [],
    "schedule": {"MON": [], "TUE": [], "WED": [], "THU": [], "FRI": []},
    "schedule_labels": {"MON": "MON", "TUE": "TUE", "WED": "WED", "THU": "THU", "FRI": "FRI"},
}

def load() -> dict:
    if os.path.exists(CONTENT_PATH):
        with open(CONTENT_PATH, encoding="utf-8") as f:
            data = json.load(f)
        for k, v in EMPTY.items():
            data.setdefault(k, v)
        return data
    return json.loads(json.dumps(EMPTY))

def save(data: dict):
    os.makedirs(os.path.dirname(CONTENT_PATH), exist_ok=True)
    with open(CONTENT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def reset():
    save(json.loads(json.dumps(EMPTY)))
    print("  ✓ content.json 초기화 완료")
