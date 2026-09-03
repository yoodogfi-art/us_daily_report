# src/us_report_daily/dates.py
import datetime as dt
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class DatePack:
    asof:  dt.date
    prev:  dt.date   # T-1
    mprev: dt.date   # 전월 (30일 전 가장 가까운 영업일)
    ytd0:  dt.date   # 연초 (1/2 또는 첫 영업일)


def parse_date(s: str) -> dt.date:
    s = str(s).strip()
    return dt.date(int(s[:4]), int(s[4:6]), int(s[6:]))


def _nearest_on_or_before(dates: list[dt.date], target: dt.date) -> dt.date:
    cands = [d for d in dates if d <= target]
    if not cands:
        return min(dates)
    return max(cands)


def build_date_pack(all_dates: list[dt.date], asof_str: str, gap: int) -> DatePack:
    asof = parse_date(asof_str)
    prev = asof - dt.timedelta(days=1 + gap)

    m_target = asof - dt.timedelta(days=30)
    y_target  = dt.date(asof.year, 1, 2)

    sorted_dates = sorted(set(all_dates))
    mprev = _nearest_on_or_before(sorted_dates, m_target)
    ytd0  = _nearest_on_or_before(
        [d for d in sorted_dates if d.year == asof.year] or sorted_dates,
        y_target,
    )

    return DatePack(asof=asof, prev=prev, mprev=mprev, ytd0=ytd0)
