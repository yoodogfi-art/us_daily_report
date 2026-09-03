# src/us_report_daily/cli.py
"""
수기입력 CLI — 위원발언 / 시황 / 경제지표 / 주간일정
"""
from . import content_store as cs

WEEKDAYS = ["MON", "TUE", "WED", "THU", "FRI"]
WEEKDAY_KR = {"MON": "월", "TUE": "화", "WED": "수", "THU": "목", "FRI": "금"}


# ── 공통 ────────────────────────────────────────────────────

def _sep(title=""):
    print("\n" + "─" * 50)
    if title:
        print(f"  {title}")
        print("─" * 50)


def _inp(prompt, default="") -> str:
    val = input(f"  {prompt}" + (f" [{default}]" if default else "") + ": ").strip()
    return val if val else default


def _multiline(prompt, current="") -> str:
    if current:
        short = current[:60] + ("..." if len(current) > 60 else "")
        print(f"  현재: {short}")
        if input("  유지? (Enter=유지 / n=새로입력): ").strip().lower() != "n":
            return current
    print(f"  {prompt}  (빈 줄 2회 → 완료)")
    lines, blank = [], 0
    while True:
        line = input()
        if line == "":
            blank += 1
            if blank >= 2:
                break
            lines.append("")
        else:
            blank = 0
            lines.append(line)
    return "\n".join(lines).strip()


# ── 섹션별 ──────────────────────────────────────────────────

def edit_speakers(data: dict):
    _sep("위원 발언")
    sp_list = data.setdefault("speakers", [])

    while True:
        if sp_list:
            print("\n  현재 등록:")
            for i, sp in enumerate(sp_list):
                print(f"    [{i}] {sp['name']} ({sp['org']})")
        print("\n  [a]추가  [e]수정  [d]삭제  [q]완료")
        cmd = input("  → ").strip().lower()
        if cmd == "q":
            break
        elif cmd == "a":
            name = _inp("이름")
            org  = _inp("소속")
            text = _multiline("발언 내용:")
            if name and text:
                sp_list.append({"name": name, "org": org, "text": text})
                print(f"  ✓ [{name}] 추가")
        elif cmd == "e" and sp_list:
            try:
                i = int(_inp(f"수정 번호 (0~{len(sp_list)-1})"))
                sp = sp_list[i]
                sp["name"] = _inp("이름", sp["name"])
                sp["org"]  = _inp("소속", sp["org"])
                sp["text"] = _multiline("발언:", sp["text"])
            except (ValueError, IndexError):
                print("  잘못된 번호")
        elif cmd == "d" and sp_list:
            try:
                i = int(_inp(f"삭제 번호 (0~{len(sp_list)-1})"))
                print(f"  ✓ [{sp_list.pop(i)['name']}] 삭제")
            except (ValueError, IndexError):
                print("  잘못된 번호")

    cs.save(data)


def edit_summary(data: dict):
    _sep("시황 Summary")
    summary = data.setdefault("summary", {})
    for key, label in [("채권", "채권시장"), ("증시", "증시"), ("유가", "유가"), ("환시", "환시")]:
        print(f"\n▶ {label}")
        summary[key] = _multiline(f"{label} 내용:", summary.get(key, ""))
    cs.save(data)


def edit_indicators(data: dict):
    _sep("주요 경제지표")
    regions = data.setdefault("indicators", [])

    while True:
        if regions:
            print("\n  현재 지역:")
            for i, r in enumerate(regions):
                print(f"    [{i}] {r['region']} ({len(r['items'])}개)")
        print("\n  [a]지역추가  [e]지역수정  [d]지역삭제  [q]완료")
        cmd = input("  → ").strip().lower()
        if cmd == "q":
            break
        elif cmd == "a":
            rname = _inp("지역명 (예: 미국)")
            items = []
            print(f"  [{rname}] 지표 입력 (이름 빈칸=종료)")
            while True:
                name = input("    지표명: ").strip()
                if not name:
                    break
                items.append({
                    "name": name,
                    "actual": _inp("Actual", "—"),
                    "survey": _inp("Survey", "—"),
                    "prior":  _inp("Prior",  "—"),
                })
            regions.append({"region": rname, "items": items})
        elif cmd == "e" and regions:
            try:
                i = int(_inp(f"번호 (0~{len(regions)-1})"))
                region = regions[i]
                region["region"] = _inp("지역명", region["region"])
                while True:
                    print(f"  지표 [{len(region['items'])}개]  [a]추가 [e]수정 [d]삭제 [q]완료")
                    ic = input("  → ").strip().lower()
                    if ic == "q":
                        break
                    elif ic == "a":
                        region["items"].append({
                            "name":   input("    지표명: ").strip(),
                            "actual": _inp("Actual", "—"),
                            "survey": _inp("Survey", "—"),
                            "prior":  _inp("Prior",  "—"),
                        })
                    elif ic == "e":
                        ji = int(_inp("번호"))
                        it = region["items"][ji]
                        it["name"]   = _inp("지표명", it["name"])
                        it["actual"] = _inp("Actual", it["actual"])
                        it["survey"] = _inp("Survey", it["survey"])
                        it["prior"]  = _inp("Prior",  it["prior"])
                    elif ic == "d":
                        region["items"].pop(int(_inp("번호")))
            except (ValueError, IndexError):
                print("  잘못된 번호")
        elif cmd == "d" and regions:
            try:
                regions.pop(int(_inp(f"번호 (0~{len(regions)-1})")))
            except (ValueError, IndexError):
                print("  잘못된 번호")

    cs.save(data)


def edit_schedule(data: dict):
    _sep("주간 일정")
    schedule = data.setdefault("schedule", {k: [] for k in WEEKDAYS})
    for k in WEEKDAYS:
        schedule.setdefault(k, [])

    # 날짜 레이블 입력 (예: 2/17~2/21)
    print("\n  날짜 레이블 입력 (Enter=기존 유지)")
    labels = data.setdefault("schedule_labels", {k: k for k in WEEKDAYS})
    for k in WEEKDAYS:
        labels[k] = _inp(f"{WEEKDAY_KR[k]}요일 날짜 (예: 2/17)", labels.get(k, k))
    data["schedule_labels"] = labels

    for k in WEEKDAYS:
        label = labels.get(k, k)
        events = schedule[k]
        _sep(f"{label} ({WEEKDAY_KR[k]})")
        if events:
            for i, ev in enumerate(events):
                hl = "★" if ev.get("highlight") else " "
                print(f"  [{i}]{hl} {ev['country']} — {ev['event']}")
        while True:
            print("  [a]추가  [d]삭제  [hl]중요토글  [n]다음")
            cmd = input("  → ").strip().lower()
            if cmd == "n":
                break
            elif cmd == "a":
                events.append({
                    "country":   _inp("국가코드 (US/KR/EU 등)").upper(),
                    "event":     _inp("이벤트명"),
                    "highlight": input("  중요? (y/N): ").strip().lower() == "y",
                })
            elif cmd == "d" and events:
                try:
                    events.pop(int(_inp(f"번호 (0~{len(events)-1})")))
                except (ValueError, IndexError):
                    pass
            elif cmd == "hl" and events:
                try:
                    i = int(_inp("번호"))
                    events[i]["highlight"] = not events[i].get("highlight", False)
                except (ValueError, IndexError):
                    pass
        schedule[k] = events

    cs.save(data)


def run_menu():
    data = cs.load()
    while True:
        _sep("수기입력 메뉴")
        print("  [1] 위원 발언")
        print("  [2] 시황 Summary")
        print("  [3] 경제지표")
        print("  [4] 주간 일정")
        print("  [q] 완료")
        cmd = input("\n  → ").strip().lower()
        if cmd == "q":
            break
        elif cmd == "1":
            edit_speakers(data)
        elif cmd == "2":
            edit_summary(data)
        elif cmd == "3":
            edit_indicators(data)
        elif cmd == "4":
            edit_schedule(data)
