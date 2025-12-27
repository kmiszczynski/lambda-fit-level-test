from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional


class Level(str, Enum):
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"


LEVEL_POINTS = {
    Level.BEGINNER: 1,
    Level.INTERMEDIATE: 2,
    Level.ADVANCED: 3,
}


@dataclass(frozen=True)
class TestResults:
    """
    Test results matching the Lambda function's DynamoDB structure.
    All field names correspond to what's stored in DynamoDB.
    """
    # LOWER
    max_squats: int
    # PUSH - separate fields instead of nested object
    pushups_type: str  # one of: "wall", "incline", "knee", "classic"
    max_push_ups: int
    # PULL
    max_reverse_snow_angels_45s: int
    # CORE
    plank_max_time_seconds: int  # stored as int in DynamoDB
    # CONDITIONING
    mountain_climbers_45s: int


def _clamp_int(x: int, lo: int = 0) -> int:
    return x if x >= lo else lo


def level_lower_from_squats(squats_60s: int) -> Level:
    reps = _clamp_int(int(squats_60s))
    if reps <= 20:
        return Level.BEGINNER
    if reps <= 40:
        return Level.INTERMEDIATE
    return Level.ADVANCED


def level_pull_from_reverse_snow_angels(reps_45s: int) -> Level:
    reps = _clamp_int(int(reps_45s))
    if reps <= 10:
        return Level.BEGINNER
    if reps <= 20:
        return Level.INTERMEDIATE
    return Level.ADVANCED


def level_core_from_plank(seconds: float) -> Level:
    sec = max(0.0, float(seconds))
    if sec < 30.0:
        return Level.BEGINNER
    if sec < 75.0:
        return Level.INTERMEDIATE
    return Level.ADVANCED


def level_cond_from_mountain_climbers(reps_45s: int) -> Level:
    reps = _clamp_int(int(reps_45s))
    if reps < 30:
        return Level.BEGINNER
    if reps <= 60:
        return Level.INTERMEDIATE
    return Level.ADVANCED


def level_push_from_pushups(pushups_type: str, max_push_ups: int) -> Level:
    """
    Rules (as previously defined):
    - Wall/Incline with >=1 rep -> BEGINNER
    - Knee with >=1 rep -> INTERMEDIATE
    - Classic 1–10 -> INTERMEDIATE
    - Classic 11+ -> ADVANCED
    Safety: if reps == 0 (even for reported variant), treat as BEGINNER.

    Args:
        pushups_type: one of "wall", "incline", "knee", "classic"
        max_push_ups: number of reps (integer >= 0)
    """
    variant = (pushups_type or "").strip().lower()
    reps = _clamp_int(int(max_push_ups))

    if reps == 0:
        return Level.BEGINNER

    if variant in {"wall", "incline"}:
        return Level.BEGINNER
    if variant == "knee":
        return Level.INTERMEDIATE
    if variant == "classic":
        return Level.ADVANCED if reps >= 11 else Level.INTERMEDIATE

    raise ValueError(
        f"Invalid push-up variant '{pushups_type}'. Expected one of: wall, incline, knee, classic."
    )


def _round_half_up(x: float) -> int:
    # round-half-up for positives (we only use positive domain here)
    return int(x + 0.5)


def compute_levels(results: TestResults) -> Dict[str, Any]:
    """
    Computes fitness levels from test results.

    Args:
        results: TestResults with field names matching DynamoDB structure

    Returns:
      {
        "per_category": {
            "LOWER": "BEGINNER|INTERMEDIATE|ADVANCED",
            "PUSH":  ...,
            "PULL":  ...,
            "CORE":  ...,
            "COND":  ...,
        },
        "global_level": "BEGINNER|INTERMEDIATE|ADVANCED",
        "global_level_raw_avg_points": float
      }

    Includes the earlier corrective rule:
      If there is at least one BEGINNER and at least one ADVANCED among category levels,
      cap the Global Fitness Level to INTERMEDIATE.
    """
    per_category: Dict[str, Level] = {
        "LOWER": level_lower_from_squats(results.max_squats),
        "PUSH": level_push_from_pushups(results.pushups_type, results.max_push_ups),
        "PULL": level_pull_from_reverse_snow_angels(results.max_reverse_snow_angels_45s),
        "CORE": level_core_from_plank(results.plank_max_time_seconds),
        "COND": level_cond_from_mountain_climbers(results.mountain_climbers_45s),
    }

    points = [LEVEL_POINTS[lvl] for lvl in per_category.values()]
    avg_points = sum(points) / len(points)

    # Map average points back to level using round-to-nearest (half-up)
    rounded = _round_half_up(avg_points)  # 1..3
    rounded = max(1, min(3, rounded))
    global_level = {1: Level.BEGINNER, 2: Level.INTERMEDIATE, 3: Level.ADVANCED}[rounded]

    # Corrective rule: prevent extreme mismatch (BEGINNER + ADVANCED) from producing ADVANCED globally
    has_beginner = any(lvl == Level.BEGINNER for lvl in per_category.values())
    has_advanced = any(lvl == Level.ADVANCED for lvl in per_category.values())
    if has_beginner and has_advanced:
        global_level = Level.INTERMEDIATE

    return {
        "per_category": {k: v.value for k, v in per_category.items()},
        "global_level": global_level.value,
        "global_level_raw_avg_points": avg_points,
    }
