# src/us_report_daily/excel_extract.py
"""
openpyxl로 엑셀에서 시계열 데이터 읽기.
- 1행: IMDH 수식 (무시)
- 2행: 헤더
- 3행: '조회요청실패' 등 당일 미확정 (날짜 없으면 스킵)
- 4행~: 날짜 내림차순 실데이터
"""
import datetime as dt
import pandas as pd
import openpyxl

from mapping import SeriesSpec, BondSpec

_CACHE: dict[str, pd.Series] = {}


def _to_date(v) -> dt.date | None:
    if v is None:
        return None
    if isinstance(v, (dt.datetime, dt.date)):
        return v.date() if isinstance(v, dt.datetime) else v
    ts = pd.to_datetime(v, errors="coerce")
    return None if pd.isna(ts) else ts.date()


def _read_col(ws, date_col: int, value_col: int,
              stop_year: int) -> pd.Series:
    """
    date_col, value_col (1-indexed) 로 시리즈 읽기.
    3행부터 시작, 날짜가 stop_year 이전이면 중단.
    """
    idx, vals = [], []
    for row in ws.iter_rows(min_row=3, values_only=True):
        raw_date = row[date_col - 1]
        d = _to_date(raw_date)
        if d is None:
            continue
        if d.year < stop_year:
            break
        raw_val = row[value_col - 1]
        try:
            v = float(raw_val)
        except (TypeError, ValueError):
            continue
        idx.append(d)
        vals.append(v)

    if not idx:
        return pd.Series(dtype=float)
    return pd.Series(vals, index=pd.Index(idx)).sort_index()


def load_series(wb: openpyxl.Workbook, spec: SeriesSpec,
                stop_year: int) -> pd.Series:
    key = f"{spec.sheet}|{spec.date_col}|{spec.value_col}"
    if key in _CACHE:
        return _CACHE[key]
    ws = wb[spec.sheet]
    s = _read_col(ws, spec.date_col, spec.value_col, stop_year)
    _CACHE[key] = s
    return s


class BondSeries:
    def __init__(self, today: pd.Series, prev: pd.Series):
        self.today = today  # 당일 확정 금리
        self.prev  = prev   # 산출일 금리 (전일)

    def _nearest(self, s: pd.Series, d: dt.date) -> float:
        cands = s[s.index <= d]
        return float(cands.iloc[-1]) if not cands.empty else float("nan")

    def value(self, d: dt.date) -> float:
        return self._nearest(self.today, d)

    def value_prev(self, d: dt.date) -> float:
        if d in self.prev.index:
            v = self.prev.loc[d]
            if not pd.isna(v):
                return float(v)
        cands = self.today[self.today.index < d]
        return float(cands.iloc[-1]) if not cands.empty else float("nan")


def load_bond(wb: openpyxl.Workbook, spec: BondSpec,
              stop_year: int) -> BondSeries:
    key = f"{spec.sheet}|{spec.date_col}|BOND"
    if key in _CACHE:
        return _CACHE[key]  # type: ignore
    ws = wb[spec.sheet]
    today_s = _read_col(ws, spec.date_col, spec.today_col, stop_year)
    prev_s  = _read_col(ws, spec.date_col, spec.prev_col,  stop_year)
    bs = BondSeries(today=today_s, prev=prev_s)
    _CACHE[key] = bs  # type: ignore
    return bs


def clear_cache():
    _CACHE.clear()
