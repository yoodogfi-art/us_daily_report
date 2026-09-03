# src/us_report_daily/mapping.py
"""
엑셀 시트 열 위치 기반 매핑.
항목 추가/변경 시 이 파일만 수정하면 됨.

[fmt]       rate_kr=소수점2, rate_us=소수점4, price=소수점3, index=소수점2+콤마, fx=소수점3+콤마
[diff_fmt]  pct2=등락률%, abs4=절대차4자리, absbp2=bp차2자리
[group]     HTML 레이아웃 카테고리 구분용
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class SeriesSpec:
    sheet: str
    date_col: int   # 1-indexed
    value_col: int


@dataclass(frozen=True)
class BondSpec:
    sheet: str
    date_col: int
    prev_col: int   # 민평3사 수익률(산출일)
    today_col: int  # 민평3사 수익률(산출일) 당일


@dataclass(frozen=True)
class ItemConfig:
    spec: SeriesSpec | BondSpec
    group: str       # 'kr_bond' | 'fx' | 'equity' | 'us_bond' | 'intl_bond' | 'commodity'
    is_bond: bool  = False
    use_diff: bool = False
    fmt: str       = "price"
    diff_fmt: str  = "pct2"


def _bond(date_col, prev_col, today_col, group="kr_bond") -> ItemConfig:
    return ItemConfig(
        spec=BondSpec(sheet="국내채권", date_col=date_col,
                      prev_col=prev_col, today_col=today_col),
        group=group, is_bond=True, use_diff=True,
        fmt="rate_kr", diff_fmt="absbp2",
    )


ITEMS: dict[str, ItemConfig] = {

    # ━━ 국내 금리 (좌측 상단) ━━━━━━━━━━━━━━━━━━━━━━━━
    "통안 2Y":      _bond(10, 11, 12, "kr_bond"),
    "국고 3Y":      _bond(1,  2,  3,  "kr_bond"),
    "국고 5Y":      _bond(4,  5,  6,  "kr_bond"),
    "국고 10Y":     _bond(7,  8,  9,  "kr_bond"),
    "국채3년선물": ItemConfig(
        spec=SeriesSpec(sheet="국내채권", date_col=16, value_col=17),
        group="kr_bond", use_diff=False, fmt="price", diff_fmt="pct2",
    ),

    # ━━ 환율 (좌측 하단) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    "USD/KRW": ItemConfig(
        spec=SeriesSpec(sheet="환율", date_col=10, value_col=13),
        group="fx", use_diff=False, fmt="fx", diff_fmt="pct2",
    ),
    "NDF": ItemConfig(
        spec=SeriesSpec(sheet="환율", date_col=19, value_col=20),
        group="fx", use_diff=False, fmt="fx", diff_fmt="pct2",
    ),
    "Dollar Index": ItemConfig(
        spec=SeriesSpec(sheet="환율", date_col=1, value_col=3),
        group="fx", use_diff=False, fmt="price", diff_fmt="pct2",
    ),
    "USD/JPY": ItemConfig(
        spec=SeriesSpec(sheet="환율", date_col=4, value_col=6),
        group="fx", use_diff=False, fmt="price", diff_fmt="pct2",
    ),
    "EUR/USD": ItemConfig(
        spec=SeriesSpec(sheet="환율", date_col=7, value_col=9),
        group="fx", use_diff=False, fmt="price", diff_fmt="pct2",
    ),
    "JPY/KRW": ItemConfig(
        spec=SeriesSpec(sheet="환율", date_col=16, value_col=18),
        group="fx", use_diff=False, fmt="fx", diff_fmt="pct2",
    ),
    "USD/CNY": ItemConfig(
        spec=SeriesSpec(sheet="환율", date_col=24, value_col=25),
        group="fx", use_diff=False, fmt="price", diff_fmt="pct2",
    ),
    "GBP/USD": ItemConfig(
        spec=SeriesSpec(sheet="환율", date_col=28, value_col=29),
        group="fx", use_diff=False, fmt="price", diff_fmt="pct2",
    ),

    # ━━ 증시 (우측 상단) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    "KOSPI": ItemConfig(
        spec=SeriesSpec(sheet="주가지수", date_col=1, value_col=2),
        group="equity", use_diff=False, fmt="index", diff_fmt="pct2",
    ),
    "NIKKEI": ItemConfig(
        spec=SeriesSpec(sheet="주가지수", date_col=5, value_col=7),
        group="equity", use_diff=False, fmt="index", diff_fmt="pct2",
    ),
    "중국상해종합": ItemConfig(
        spec=SeriesSpec(sheet="지수", date_col=1, value_col=2),
        group="equity", use_diff=False, fmt="index", diff_fmt="pct2",
    ),
    "DOW": ItemConfig(
        spec=SeriesSpec(sheet="주가지수", date_col=9, value_col=11),
        group="equity", use_diff=False, fmt="index", diff_fmt="pct2",
    ),
    "S&P500": ItemConfig(
        spec=SeriesSpec(sheet="주가지수", date_col=13, value_col=15),
        group="equity", use_diff=False, fmt="index", diff_fmt="pct2",
    ),
    "NASDAQ": ItemConfig(
        spec=SeriesSpec(sheet="주가지수", date_col=15, value_col=17),
        group="equity", use_diff=False, fmt="index", diff_fmt="pct2",
    ),

    # ━━ 미국 채권 (우측 중단) ━━━━━━━━━━━━━━━━━━━━━━━
    "T-Note (2yr)": ItemConfig(
        spec=SeriesSpec(sheet="해외채권", date_col=1, value_col=3),
        group="us_bond", use_diff=True, fmt="rate_us", diff_fmt="abs4",
    ),
    "T-Note (10yr)": ItemConfig(
        spec=SeriesSpec(sheet="해외채권", date_col=6, value_col=8),
        group="us_bond", use_diff=True, fmt="rate_us", diff_fmt="abs4",
    ),
    "T-Bill (30yr)": ItemConfig(
        spec=SeriesSpec(sheet="해외채권", date_col=11, value_col=13),
        group="us_bond", use_diff=True, fmt="rate_us", diff_fmt="abs4",
    ),

    # ━━ 해외 금리 (우측 중단 - 이어서) ━━━━━━━━━━━━━━━━
    "독일 10Y": ItemConfig(
        spec=SeriesSpec(sheet="해외채권", date_col=16, value_col=18),
        group="intl_bond", use_diff=True, fmt="rate_us", diff_fmt="abs4",
    ),
    "영국 10Y": ItemConfig(
        spec=SeriesSpec(sheet="해외채권", date_col=21, value_col=23),
        group="intl_bond", use_diff=True, fmt="rate_us", diff_fmt="abs4",
    ),
    "일본 10Y": ItemConfig(
        spec=SeriesSpec(sheet="해외채권", date_col=26, value_col=28),
        group="intl_bond", use_diff=True, fmt="rate_us", diff_fmt="abs4",
    ),

    # ━━ 원자재 / 기타 (우측 하단) ━━━━━━━━━━━━━━━━━━━
    "WTI": ItemConfig(
        spec=SeriesSpec(sheet="원자재", date_col=1, value_col=3),
        group="commodity", use_diff=False, fmt="price", diff_fmt="pct2",
    ),
    "GOLD": ItemConfig(
        spec=SeriesSpec(sheet="원자재", date_col=10, value_col=11),
        group="commodity", use_diff=False, fmt="price", diff_fmt="pct2",
    ),
    "SOFR": ItemConfig(
        spec=SeriesSpec(sheet="외환", date_col=5, value_col=6),
        group="commodity", use_diff=True, fmt="rate_us", diff_fmt="abs4",
    ),
    "TED spread": ItemConfig(
        spec=SeriesSpec(sheet="지수", date_col=27, value_col=28),
        group="commodity", use_diff=True, fmt="price", diff_fmt="abs4",
    ),
}
