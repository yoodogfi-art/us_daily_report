# src/us_report_daily/config.py
"""
★ 파일 경로 설정 — 경로 변경 시 여기만 수정
"""
import os

# src/us_report_daily/config.py → ../../ = 프로젝트 루트
_ROOT = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "../..", "..")
)

XLSX_PATH     = os.path.join(_ROOT, "us_data.xlsx")
TEMPLATE_PATH = os.path.join(_ROOT, "../templates", "templates/template.html")
CONTENT_PATH  = os.path.join(_ROOT, "content", "content.json")
OUTPUT_DIR    = os.path.join(_ROOT, "output")
