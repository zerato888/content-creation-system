# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Evidence-based "next step" suggestions. Deterministic rules, no LLM, no invented
numbers: every suggestion names the data it read. A rule that finds nothing emits
nothing; absence of a signal is never reported as "all good"."""
import datetime as dt

from cc.config import config
from cc.server import creator, lab, life

STALLED_AFTER_DAYS = 5


def _parse(iso):
    try:
        parsed = dt.datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=dt.timezone.utc)


def stalled_lab_pieces(root, cfg):
    now, out = dt.datetime.now(dt.timezone.utc), []
    for brand in config.active_brands(cfg):
        for item in lab.list_items(root, brand["id"]):
            if item.get("archivada") or (item.get("final_video") or {}).get("qc_verdict") == "PASS":
                continue
            updated = _parse(item.get("actualizado") or item.get("creado") or "")
            if updated and (days := (now - updated).days) >= STALLED_AFTER_DAYS:
                out.append({"brand": brand["id"], "kind": "stalled_piece",
                            "text": f"Sin avance hace {days} días: {item.get('tema') or item.get('id')}",
                            "source": f"/api/lab/items?brand={brand['id']}"})
    return out


def weekly_goal_gap(root, cfg):
    s = creator.summary(root, cfg)
    if s["remaining"] == 0:
        return []
    return [{"brand": None, "kind": "weekly_goal",
             "text": f"Esta semana llevás {s['this_week']} de {s['goal']} videos: faltan {s['remaining']}",
             "source": "/api/creator/summary"}]


def income_pace_gap(root, cfg):
    goal = cfg["vida"]["income_goal"]
    if not config.enabled(cfg, "vida") or not goal:
        return []
    today = config.today(cfg)
    view = life.income_month_view(root, cfg, today.year, today.month)
    days_in_month = (dt.date(today.year + today.month // 12, today.month % 12 + 1, 1) - dt.timedelta(days=1)).day
    pct, expected = view["total_recibido"] / goal * 100, today.day / days_in_month * 100
    if pct >= expected - 10:  # within 10 points of pace: not worth flagging
        return []
    return [{"brand": None, "kind": "income_pace",
             "text": f"Ingresos al {pct:.0f}% de la meta del mes, con {today.day} de {days_in_month} días "
                     f"(ritmo esperado ~{expected:.0f}%)", "source": "/api/life/income"}]


RULES = (stalled_lab_pieces, weekly_goal_gap, income_pace_gap)


def run(root, cfg):
    items = [item for rule in RULES for item in rule(root, cfg)]
    return {"generated_at": dt.datetime.now(dt.timezone.utc).isoformat(), "count": len(items), "items": items}
