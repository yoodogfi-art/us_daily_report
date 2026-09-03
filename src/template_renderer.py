# src/us_report_daily/template_renderer.py
import re, html as _html
from config import TEMPLATE_PATH
from src import content_store as cs


def _speakers_html(speakers: list) -> str:
    if not speakers:
        return '<div class="cm-item"><div class="cm-tx" contenteditable="true">발언 내용 입력...</div></div>'
    parts = []
    for sp in speakers:
        parts.append(
            f'<div class="cm-item">'
            f'<div class="cm-meta">'
            f'<span class="cm-name" contenteditable="true">{_html.escape(sp.get("name",""))}</span>'
            f'<span class="cm-org"  contenteditable="true">{_html.escape(sp.get("org",""))}</span>'
            f'<button class="cm-del" onclick="this.closest(\'.cm-item\').remove()">&#x2715;</button>'
            f'</div>'
            f'<div class="cm-tx" contenteditable="true">{_html.escape(sp.get("text",""))}</div>'
            f'</div>'
        )
    return "\n".join(parts)


def _indicators_html(regions: list) -> str:
    """국가를 별도 행 없이 각 지표의 첫 번째 td에 rowspan으로 표시"""
    rows = []
    for region in regions:
        country = _html.escape(region.get("region", ""))
        items   = region.get("items", [])
        if not items:
            continue
        rspan = len(items)
        for idx, it in enumerate(items):
            actual = it.get("actual", "—")
            try:
                float(str(actual).replace(",", "").replace("%", ""))
                a_cls = "v"
            except ValueError:
                a_cls = "fl"

            if idx == 0:
                country_td = (
                    f'<td class="ind-country" rowspan="{rspan}" contenteditable="true">'
                    f'{country}</td>'
                )
            else:
                country_td = ""

            rows.append(
                f'<tr class="ind-row">'
                f'{country_td}'
                f'<td contenteditable="true">{_html.escape(it.get("name",""))}</td>'
                f'<td class="{a_cls}" contenteditable="true">{_html.escape(actual)}</td>'
                f'<td class="fl" contenteditable="true">{_html.escape(it.get("survey","—"))}</td>'
                f'<td class="fl" contenteditable="true">{_html.escape(it.get("prior","—"))}</td>'
                f'<td class="del-cell"><button class="del-btn" onclick="removeIndRow(this)">&#x2715;</button></td>'
                f'</tr>'
            )
    if not rows:
        rows.append('<tr><td colspan="6" class="fl ind-empty" contenteditable="true">—</td></tr>')
    return "\n".join(rows)


def _schedule_html(schedule: dict, labels: dict) -> str:
    DAYS = ["MON", "TUE", "WED", "THU", "FRI"]
    parts = []
    for k in DAYS:
        date_label = labels.get(k, k)
        events     = schedule.get(k, [])
        entries    = ""
        for ev in events:
            hl = " hl" if ev.get("highlight") else ""
            entries += (
                f'<div class="sched-entry">'
                f'<span class="sched-co" contenteditable="true">{_html.escape(ev.get("country",""))}</span>'
                f'<span class="sched-ev-nm{hl}" contenteditable="true">{_html.escape(ev.get("event",""))}</span>'
                f'</div>'
            )
        if not entries:
            entries = '<div class="sched-entry"><span class="sched-co"></span><span class="sched-ev-nm fl" contenteditable="true">—</span></div>'
        parts.append(
            f'<div class="sched-day-col">'
            f'<div class="sched-day-hd">'
            f'<span class="sched-day-dt" contenteditable="true">{_html.escape(date_label)}</span>'
            f'<span class="sched-day-dw">{k}</span>'
            f'</div>{entries}</div>'
        )
    return "\n".join(parts)


def render(market: dict, asof_str: str, weekday_kr: str,
           template_path: str | None = None) -> str:
    tpl = template_path or TEMPLATE_PATH
    with open(tpl, encoding="utf-8") as f:
        html = f.read()

    content   = cs.load()
    summary   = content.get("summary", {})
    schedule  = content.get("schedule", {})
    labels    = content.get("schedule_labels", {})
    지표시황   = content.get("지표시황", "")

    d = asof_str
    date_str = f"{d[:4]}. {d[4:6]}. {d[6:]}"

    ph = dict(market)
    ph.update({
        "REPORT_DATE":     date_str,
        "REPORT_WEEKDAY":  weekday_kr,
        "SPEAKERS_HTML":   _speakers_html(content.get("speakers", [])),
        "INDICATORS_HTML": _indicators_html(content.get("indicators", [])),
        "SCHEDULE_HTML":   _schedule_html(schedule, labels),
        "SUM_채권":  _html.escape(summary.get("채권", "")),
        "SUM_증시":  _html.escape(summary.get("증시", "")),
        "SUM_유가":  _html.escape(summary.get("유가", "")),
        "SUM_환시":  _html.escape(summary.get("환시", "")),
        "지표시황":   _html.escape(지표시황),
    })

    for key, val in ph.items():
        html = html.replace("{{" + key + "}}", val)

    html = re.sub(r'\{\{CLS\|[^}]+\}\}', 'fl', html)
    html = re.sub(r'\{\{[^}]+\}\}',      '—',  html)
    return html
