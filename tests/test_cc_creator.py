# SPDX-License-Identifier: LicenseRef-PolyForm-Noncommercial-1.0.0
"""Weekly streak math (goal 3, grace 1), views at 48h and the weekly hook winner."""
import datetime as dt
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from cc.config import config  # noqa: E402
from cc.server import creator  # noqa: E402

D = dt.date.fromisoformat
# Mondays: 2026-03-02, 03-09, 03-16, 03-23


def s(dates, today, goal=3, grace=1):
    return creator.streak([D(x) for x in dates], D(today), goal, grace)


def test_no_recordings():
    r = s([], "2026-03-18")
    assert r["streak_weeks"] == 0 and r["this_week"] == 0 and r["remaining"] == 3


def test_current_week_counts_only_once_met():
    assert s(["2026-03-16", "2026-03-17"], "2026-03-18")["streak_weeks"] == 0
    r = s(["2026-03-16", "2026-03-17", "2026-03-18"], "2026-03-18")
    assert r["streak_weeks"] == 1 and r["remaining"] == 0


def test_consecutive_weeks_and_break():
    met_week1 = ["2026-03-03", "2026-03-04", "2026-03-05"]
    met_week2 = ["2026-03-10", "2026-03-11", "2026-03-12"]
    # in progress this week (1 of 3) does not break two met weeks
    assert s(met_week1 + met_week2 + ["2026-03-17"], "2026-03-18")["streak_weeks"] == 2
    # a short week in between breaks it
    assert s(met_week1 + ["2026-03-10"] + ["2026-03-17", "2026-03-18", "2026-03-19"],
             "2026-03-19")["streak_weeks"] == 1


def test_grace_day_moves_monday_video_to_short_previous_week():
    dates = ["2026-03-10", "2026-03-11", "2026-03-16"]  # 2 in week 03-09, Monday 03-16 rescues it
    r = s(dates, "2026-03-18")
    assert r["streak_weeks"] == 1 and r["this_week"] == 0
    # with no grace the Monday video stays in its own week
    assert s(dates, "2026-03-18", grace=0)["streak_weeks"] == 0
    # an empty previous week is not rescued by stealing from the new one
    assert s(["2026-03-16", "2026-03-17", "2026-03-18"], "2026-03-18")["this_week"] == 3
    # grace never steals from a week that already met the goal
    counts = creator.week_counts([D(x) for x in ["2026-03-10", "2026-03-11", "2026-03-12", "2026-03-16"]], 3, 1)
    assert counts == {D("2026-03-09"): 3, D("2026-03-16"): 1}


def test_previous_week_pending_during_grace_does_not_break():
    two_weeks_ago = ["2026-03-03", "2026-03-04", "2026-03-05"]
    last_week_short = ["2026-03-10"]
    # Monday: last week can still be rescued, so the streak keeps the older met week
    assert s(two_weeks_ago + last_week_short, "2026-03-16")["streak_weeks"] == 1
    # Tuesday: grace is over, last week broke it
    assert s(two_weeks_ago + last_week_short, "2026-03-17")["streak_weeks"] == 0


def test_views_and_hook_winner(tmp_path):
    root, cfg = str(tmp_path), config.normalize({})
    a = creator.add_recording(root, cfg, {"title": "Video A", "hook": "Hook A", "date": "2026-03-16"})
    b = creator.add_recording(root, cfg, {"title": "Video B", "hook": "Hook B", "date": "2026-03-17"})
    creator.add_recording(root, cfg, {"title": "Video C", "hook": "Hook C", "date": "2026-03-10"})
    assert creator.hook_winner(root, cfg, "2026-03-18")["winner"] is None
    creator.set_views(root, a["id"], 1200)
    creator.set_views(root, b["id"], 5400)
    week = creator.hook_winner(root, cfg, "2026-03-20")
    assert week["winner"]["hook"] == "Hook B" and week["measured"] == 2 and week["week_start"] == "2026-03-16"
    for bad in (-1, "10", True, 1.5):
        with pytest.raises(ValueError):
            creator.set_views(root, a["id"], bad)
    with pytest.raises(FileNotFoundError):
        creator.set_views(root, 999, 1)
    with pytest.raises(ValueError):
        creator.add_recording(root, cfg, {"title": ""})
    assert creator.summary(root, config.normalize({"creator": {"weekly_goal": 5}}))["goal"] == 5
