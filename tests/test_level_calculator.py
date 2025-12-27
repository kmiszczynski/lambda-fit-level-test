import pytest
from level_calculator import (
    Level,
    TestResults,
    level_lower_from_squats,
    level_pull_from_reverse_snow_angels,
    level_core_from_plank,
    level_cond_from_mountain_climbers,
    level_push_from_pushups,
    compute_levels,
)


class TestLevelFunctions:
    """Test individual level calculation functions."""

    def test_level_lower_from_squats(self):
        """Test squat level calculation."""
        assert level_lower_from_squats(10) == Level.BEGINNER
        assert level_lower_from_squats(20) == Level.BEGINNER
        assert level_lower_from_squats(21) == Level.INTERMEDIATE
        assert level_lower_from_squats(40) == Level.INTERMEDIATE
        assert level_lower_from_squats(41) == Level.ADVANCED
        assert level_lower_from_squats(100) == Level.ADVANCED

    def test_level_pull_from_reverse_snow_angels(self):
        """Test reverse snow angels level calculation."""
        assert level_pull_from_reverse_snow_angels(5) == Level.BEGINNER
        assert level_pull_from_reverse_snow_angels(10) == Level.BEGINNER
        assert level_pull_from_reverse_snow_angels(11) == Level.INTERMEDIATE
        assert level_pull_from_reverse_snow_angels(20) == Level.INTERMEDIATE
        assert level_pull_from_reverse_snow_angels(21) == Level.ADVANCED
        assert level_pull_from_reverse_snow_angels(50) == Level.ADVANCED

    def test_level_core_from_plank(self):
        """Test plank level calculation."""
        assert level_core_from_plank(15) == Level.BEGINNER
        assert level_core_from_plank(29) == Level.BEGINNER
        assert level_core_from_plank(30) == Level.INTERMEDIATE
        assert level_core_from_plank(74) == Level.INTERMEDIATE
        assert level_core_from_plank(75) == Level.ADVANCED
        assert level_core_from_plank(120) == Level.ADVANCED

    def test_level_cond_from_mountain_climbers(self):
        """Test mountain climbers level calculation."""
        assert level_cond_from_mountain_climbers(15) == Level.BEGINNER
        assert level_cond_from_mountain_climbers(29) == Level.BEGINNER
        assert level_cond_from_mountain_climbers(30) == Level.INTERMEDIATE
        assert level_cond_from_mountain_climbers(60) == Level.INTERMEDIATE
        assert level_cond_from_mountain_climbers(61) == Level.ADVANCED
        assert level_cond_from_mountain_climbers(100) == Level.ADVANCED

    def test_level_push_from_pushups_zero_reps(self):
        """Test that zero reps always returns BEGINNER."""
        assert level_push_from_pushups("classic", 0) == Level.BEGINNER
        assert level_push_from_pushups("knee", 0) == Level.BEGINNER
        assert level_push_from_pushups("wall", 0) == Level.BEGINNER

    def test_level_push_from_pushups_wall(self):
        """Test wall push-ups level calculation."""
        assert level_push_from_pushups("wall", 1) == Level.BEGINNER
        assert level_push_from_pushups("wall", 10) == Level.BEGINNER
        assert level_push_from_pushups("wall", 50) == Level.BEGINNER

    def test_level_push_from_pushups_incline(self):
        """Test incline push-ups level calculation."""
        assert level_push_from_pushups("incline", 1) == Level.BEGINNER
        assert level_push_from_pushups("incline", 10) == Level.BEGINNER
        assert level_push_from_pushups("incline", 50) == Level.BEGINNER

    def test_level_push_from_pushups_knee(self):
        """Test knee push-ups level calculation."""
        assert level_push_from_pushups("knee", 1) == Level.INTERMEDIATE
        assert level_push_from_pushups("knee", 10) == Level.INTERMEDIATE
        assert level_push_from_pushups("knee", 50) == Level.INTERMEDIATE

    def test_level_push_from_pushups_classic(self):
        """Test classic push-ups level calculation."""
        assert level_push_from_pushups("classic", 1) == Level.INTERMEDIATE
        assert level_push_from_pushups("classic", 10) == Level.INTERMEDIATE
        assert level_push_from_pushups("classic", 11) == Level.ADVANCED
        assert level_push_from_pushups("classic", 50) == Level.ADVANCED

    def test_level_push_from_pushups_invalid_variant(self):
        """Test that invalid variant raises ValueError."""
        with pytest.raises(ValueError, match="Invalid push-up variant"):
            level_push_from_pushups("invalid", 10)


class TestComputeLevels:
    """Test the complete level computation."""

    def test_all_beginner(self):
        """Test all exercises at beginner level."""
        results = TestResults(
            max_squats=10,
            pushups_type="wall",
            max_push_ups=5,
            max_reverse_snow_angels_45s=5,
            plank_max_time_seconds=20,
            mountain_climbers_45s=15,
        )
        levels = compute_levels(results)

        assert levels["global_level"] == "BEGINNER"
        assert levels["per_category"]["LOWER"] == "BEGINNER"
        assert levels["per_category"]["PUSH"] == "BEGINNER"
        assert levels["per_category"]["PULL"] == "BEGINNER"
        assert levels["per_category"]["CORE"] == "BEGINNER"
        assert levels["per_category"]["COND"] == "BEGINNER"

    def test_all_advanced(self):
        """Test all exercises at advanced level."""
        results = TestResults(
            max_squats=50,
            pushups_type="classic",
            max_push_ups=15,
            max_reverse_snow_angels_45s=25,
            plank_max_time_seconds=90,
            mountain_climbers_45s=70,
        )
        levels = compute_levels(results)

        assert levels["global_level"] == "ADVANCED"
        assert levels["per_category"]["LOWER"] == "ADVANCED"
        assert levels["per_category"]["PUSH"] == "ADVANCED"
        assert levels["per_category"]["PULL"] == "ADVANCED"
        assert levels["per_category"]["CORE"] == "ADVANCED"
        assert levels["per_category"]["COND"] == "ADVANCED"

    def test_mixed_intermediate(self):
        """Test mixed levels averaging to intermediate."""
        results = TestResults(
            max_squats=25,
            pushups_type="knee",
            max_push_ups=10,
            max_reverse_snow_angels_45s=15,
            plank_max_time_seconds=50,
            mountain_climbers_45s=45,
        )
        levels = compute_levels(results)

        assert levels["global_level"] == "INTERMEDIATE"

    def test_corrective_rule_beginner_and_advanced(self):
        """Test corrective rule: BEGINNER + ADVANCED = INTERMEDIATE globally."""
        results = TestResults(
            max_squats=5,  # BEGINNER
            pushups_type="classic",
            max_push_ups=20,  # ADVANCED
            max_reverse_snow_angels_45s=50,  # ADVANCED
            plank_max_time_seconds=100,  # ADVANCED
            mountain_climbers_45s=80,  # ADVANCED
        )
        levels = compute_levels(results)

        # Should be capped at INTERMEDIATE due to beginner + advanced mix
        assert levels["global_level"] == "INTERMEDIATE"
        assert levels["per_category"]["LOWER"] == "BEGINNER"
        assert levels["per_category"]["PUSH"] == "ADVANCED"

    def test_real_world_example(self):
        """Test with realistic test results."""
        results = TestResults(
            max_squats=30,
            pushups_type="classic",
            max_push_ups=8,
            max_reverse_snow_angels_45s=12,
            plank_max_time_seconds=45,
            mountain_climbers_45s=40,
        )
        levels = compute_levels(results)

        assert levels["per_category"]["LOWER"] == "INTERMEDIATE"  # 30 squats
        assert levels["per_category"]["PUSH"] == "INTERMEDIATE"  # classic 8 reps
        assert levels["per_category"]["PULL"] == "INTERMEDIATE"  # 12 angels
        assert levels["per_category"]["CORE"] == "INTERMEDIATE"  # 45s plank
        assert levels["per_category"]["COND"] == "INTERMEDIATE"  # 40 climbers
        assert levels["global_level"] == "INTERMEDIATE"

    def test_average_points_calculation(self):
        """Test that raw average points are calculated correctly."""
        results = TestResults(
            max_squats=10,  # BEGINNER = 1 point
            pushups_type="classic",
            max_push_ups=15,  # ADVANCED = 3 points
            max_reverse_snow_angels_45s=15,  # INTERMEDIATE = 2 points
            plank_max_time_seconds=50,  # INTERMEDIATE = 2 points
            mountain_climbers_45s=45,  # INTERMEDIATE = 2 points
        )
        levels = compute_levels(results)

        # Average = (1 + 3 + 2 + 2 + 2) / 5 = 10 / 5 = 2.0
        assert levels["global_level_raw_avg_points"] == 2.0