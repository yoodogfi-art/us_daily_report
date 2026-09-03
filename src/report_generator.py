# src/us_report_daily/report_generator.py
import math
import openpyxl
from config import XLSX_PATH
from mapping import ITEMS
from src.excel_extract import load_series, load_bond, clear_cache
from src.dates import DatePack, build_date_pack
from src.calc import metrics_series, metrics_bond


def _nan(v) -> bool:
    try: return v is None or math.isnan(float(v))
    except: return True

def fmt_t0(v, fmt: str) -> str:
    if _nan(v): return "—"
    f = float(v)
    return {"rate_kr": f"{f:.2f}", "rate_us": f"{f:.4f}",
            "price": f"{f:.3f}", "index": f"{f:,.2f}", "fx": f"{f:,.3f}"}.get(fmt, f"{f:.3f}")

def fmt_diff(v, diff_fmt: str) -> tuple[str, str]:
    if _nan(v): return "—", "fl"
    f = float(v)
    s = {"pct2": f"{f:+.2f}%", "abs4": f"{f:+.4f}", "absbp2": f"{f:+.2f}"}.get(diff_fmt, f"{f:+.4f}")
    return s, ("p" if f > 0 else ("n" if f < 0 else "fl"))


def build_placeholders(asof_str: str, gap: int,
                       xlsx_path: str | None = None) -> tuple[dict, DatePack]:
    path = xlsx_path or XLSX_PATH
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    stop_year = int(asof_str[:4])
    clear_cache()

    bond_data, series_data, errors = {}, {}, []
    for item, cfg in ITEMS.items():
        try:
            if cfg.is_bond:
                bond_data[item] = load_bond(wb, cfg.spec, stop_year)
            else:
                series_data[item] = load_series(wb, cfg.spec, stop_year)
        except Exception as e:
            errors.append(f"  [{item}]: {e}")

    if errors:
        print("[경고] 로드 실패:")
        for e in errors: print(e)

    all_dates = sorted(
        {d for s in series_data.values() for d in s.index} |
        {d for bs in bond_data.values()  for d in bs.today.index}
    )
    if not all_dates:
        raise RuntimeError("유효한 데이터 없음")

    dp = build_date_pack(all_dates, asof_str, gap)
    print(f"[날짜] T0={dp.asof}  T-1={dp.prev}  1M={dp.mprev}  YTD={dp.ytd0}")

    result: dict[str, str] = {}
    for item, cfg in ITEMS.items():
        if cfg.is_bond and item in bond_data:
            m = metrics_bond(bond_data[item], dp)
        elif not cfg.is_bond and item in series_data:
            m = metrics_series(series_data[item], dp, cfg.use_diff)
        else:
            m = {"T0": None, "1D": None, "1M": None, "YTD": None}

        t0_str = fmt_t0(m["T0"], cfg.fmt)
        result[f"{item}|T0"]     = t0_str
        result[f"CLS|{item}|T0"] = "v" if t0_str != "—" else "fl"
        for col in ["1D", "1M", "YTD"]:
            val_str, cls = fmt_diff(m[col], cfg.diff_fmt)
            result[f"{item}|{col}"]     = val_str
            result[f"CLS|{item}|{col}"] = cls

    wb.close()
    return result, dp
