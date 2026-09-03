# run.py — 통합 실행 진입점
"""
사용법:
    python run.py
    python run.py --asof 20260220 --gap 0
    python run.py --asof 20260220 --skip-input
"""
import os, sys, argparse, datetime as dt, webbrowser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

from src import content_store as cs
from us_rep.config import XLSX_PATH, OUTPUT_DIR
from us_rep.cli import run_menu
from us_report_daily.report_generator import build_placeholders
from us_report_daily.template_renderer import render

WEEKDAY_KR = ["월요일","화요일","수요일","목요일","금요일","토요일","일요일"]

def _sep(t=""):
    print("\n"+"═"*52)
    if t: print(f"  {t}"); print("═"*52)

def _ask_asof() -> str:
    today = dt.date.today().strftime("%Y%m%d")
    while True:
        v = input(f"\n  기준일 (YYYYMMDD) [{today}]: ").strip() or today
        if len(v)==8 and v.isdigit():
            try: dt.date(int(v[:4]),int(v[4:6]),int(v[6:])); return v
            except: pass
        print("  ✗ 형식 오류")

def _ask_gap() -> int:
    print("\n  전영업일 갭  0=평일 / 2=월요일 / 1=공휴일")
    v = input("  gap [0]: ").strip()
    return int(v) if v.isdigit() else 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--asof", default=None)
    parser.add_argument("--gap",  type=int, default=None)
    parser.add_argument("--skip-input", action="store_true")
    args = parser.parse_args()

    _sep("US Report Daily")
    if not os.path.exists(XLSX_PATH):
        print(f"\n  [경고] 엑셀 파일 없음: {XLSX_PATH}")
        print("  src/us_report_daily/config.py 에서 XLSX_PATH 수정")

    asof_str = args.asof or _ask_asof()
    gap      = args.gap  if args.gap is not None else _ask_gap()

    if not args.skip_input:
        if input("\n  수기입력 하시겠습니까? (Y/n): ").strip().lower() != "n":
            if input("  오늘자로 데이터 초기화 하시겠습니까? (Y/n): ").strip().lower() != "n":
                cs.reset()
            run_menu()

    _sep("레포트 생성 중...")
    try:
        market, dp = build_placeholders(asof_str, gap)
    except Exception as e:
        print(f"\n  [오류] {e}"); sys.exit(1)

    weekday_str = WEEKDAY_KR[dp.asof.weekday()]
    html_out    = render(market, asof_str, weekday_str)

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, f"report_{asof_str}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_out)

    _sep("완료")
    print(f"  ✓ {out_path}")
    print(f"  T0={dp.asof} | T-1={dp.prev} | 1M={dp.mprev} | YTD={dp.ytd0}")

    if input("\n  브라우저로 여시겠습니까? (Y/n): ").strip().lower() != "n":
        webbrowser.open(f"file:///{out_path.replace(os.sep, '/')}")

if __name__ == "__main__":
    main()
