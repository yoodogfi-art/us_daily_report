# src/us_report_daily/calc.py
import datetime as dt
import math
import pandas as pd
from dates import DatePack
from excel_extract import BondSeries


def _nearest(s: pd.Series, d: dt.date) -> float:
    cands = s[s.index <= d]
    return float(cands.iloc[-1]) if not cands.empty else float("nan")


def _ytd_val(s: pd.Series, ytd0: dt.date) -> float:
    year_data = s[[d for d in s.index if d.year == ytd0.year]]
    cands = year_data[year_data.index <= ytd0]
    if not cands.empty:
        return float(cands.iloc[-1])
    if not year_data.empty:
        return float(year_data.sort_index().iloc[0])
    return float("nan")


def pct(curr: float, base: float) -> float:
    if math.isnan(base) or base == 0:
        return float("nan")
    return (curr / base - 1.0) * 100.0


def diff(curr: float, base: float) -> float:
    return curr - base


def metrics_series(s: pd.Series, dp: DatePack, use_diff: bool) -> dict:
    t0    = _nearest(s, dp.asof)
    tprev = _nearest(s, dp.prev)
    tm    = _nearest(s, dp.mprev)
    ty    = _ytd_val(s, dp.ytd0)
    fn    = diff if use_diff else pct
    return {
        "T0":  None if math.isnan(t0) else t0,
        "1D":  None if math.isnan(t0) else fn(t0, tprev),
        "1M":  None if math.isnan(t0) else fn(t0, tm),
        "YTD": None if math.isnan(t0) else fn(t0, ty),
    }


def metrics_bond(bs: BondSeries, dp: DatePack) -> dict:
    t0    = bs.value(dp.asof)
    tprev = bs.value_prev(dp.asof)
    tm    = _nearest(bs.today, dp.mprev)
    ty    = _ytd_val(bs.today, dp.ytd0)
    return {
        "T0":  None if math.isnan(t0) else t0,
        "1D":  None if math.isnan(t0) else diff(t0, tprev),
        "1M":  None if math.isnan(t0) else diff(t0, tm),
        "YTD": None if math.isnan(t0) else diff(t0, ty),
    }
