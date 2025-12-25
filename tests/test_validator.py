import pytest
from validator import validate_fitness_test_request


class TestValidateFitnessTestRequest:
    """Tests for the fitness test request validator."""

    def test_valid_request(self):
        """Test validation with a valid request."""
        body = {
            "user_id": "user123",
            "pushups_type": "classic",
            "results": {
                "max_push_ups": 50,
                "max_squats": 100,
                "max_reverse_snow_angels_45s": 30,
                "plank_max_time_seconds": 120,
                "mountain_climbers_45s": 80
            }
        }
        is_valid, error = validate_fitness_test_request(body)
        assert is_valid is True
        assert error == ""

    def test_missing_user_id(self):
        """Test validation when user_id is missing."""
        body = {
            "pushups_type": "classic",
            "results": {
                "max_push_ups": 50,
                "max_squats": 100,
                "max_reverse_snow_angels_45s": 30,
                "plank_max_time_seconds": 120,
                "mountain_climbers_45s": 80
            }
        }
        is_valid, error = validate_fitness_test_request(body)
        assert is_valid is False
        assert "user_id" in error

    def test_missing_results(self):
        """Test validation when results object is missing."""
        body = {
            "user_id": "user123",
            "pushups_type": "classic"
        }
        is_valid, error = validate_fitness_test_request(body)
        assert is_valid is False
        assert "results" in error

    def test_empty_user_id(self):
        """Test validation with empty user_id."""
        body = {
            "user_id": "",
            "pushups_type": "classic",
            "results": {
                "max_push_ups": 50,
                "max_squats": 100,
                "max_reverse_snow_angels_45s": 30,
                "plank_max_time_seconds": 120,
                "mountain_climbers_45s": 80
            }
        }
        is_valid, error = validate_fitness_test_request(body)
        assert is_valid is False
        assert "user_id" in error

    def test_missing_result_field(self):
        """Test validation when a result field is missing."""
        body = {
            "user_id": "user123",
            "pushups_type": "classic",
            "results": {
                "max_push_ups": 50,
                "max_squats": 100,
                "max_reverse_snow_angels_45s": 30,
                "plank_max_time_seconds": 120
                # mountain_climbers_45s is missing
            }
        }
        is_valid, error = validate_fitness_test_request(body)
        assert is_valid is False
        assert "mountain_climbers_45s" in error

    def test_non_integer_result_value(self):
        """Test validation with non-integer result value."""
        body = {
            "user_id": "user123",
            "pushups_type": "classic",
            "results": {
                "max_push_ups": "fifty",
                "max_squats": 100,
                "max_reverse_snow_angels_45s": 30,
                "plank_max_time_seconds": 120,
                "mountain_climbers_45s": 80
            }
        }
        is_valid, error = validate_fitness_test_request(body)
        assert is_valid is False
        assert "integer" in error

    def test_negative_result_value(self):
        """Test validation with negative result value."""
        body = {
            "user_id": "user123",
            "pushups_type": "classic",
            "results": {
                "max_push_ups": -5,
                "max_squats": 100,
                "max_reverse_snow_angels_45s": 30,
                "plank_max_time_seconds": 120,
                "mountain_climbers_45s": 80
            }
        }
        is_valid, error = validate_fitness_test_request(body)
        assert is_valid is False
        assert "non-negative" in error

    def test_zero_values_allowed(self):
        """Test that zero values are valid."""
        body = {
            "user_id": "user123",
            "pushups_type": "classic",
            "results": {
                "max_push_ups": 0,
                "max_squats": 0,
                "max_reverse_snow_angels_45s": 0,
                "plank_max_time_seconds": 0,
                "mountain_climbers_45s": 0
            }
        }
        is_valid, error = validate_fitness_test_request(body)
        assert is_valid is True
        assert error == ""

    def test_missing_pushups_type(self):
        """Test validation when pushups_type is missing."""
        body = {
            "user_id": "user123",
            "results": {
                "max_push_ups": 50,
                "max_squats": 100,
                "max_reverse_snow_angels_45s": 30,
                "plank_max_time_seconds": 120,
                "mountain_climbers_45s": 80
            }
        }
        is_valid, error = validate_fitness_test_request(body)
        assert is_valid is False
        assert "pushups_type" in error

    def test_invalid_pushups_type(self):
        """Test validation with invalid pushups_type value."""
        body = {
            "user_id": "user123",
            "pushups_type": "invalid_type",
            "results": {
                "max_push_ups": 50,
                "max_squats": 100,
                "max_reverse_snow_angels_45s": 30,
                "plank_max_time_seconds": 120,
                "mountain_climbers_45s": 80
            }
        }
        is_valid, error = validate_fitness_test_request(body)
        assert is_valid is False
        assert "pushups_type must be one of" in error

    def test_non_string_pushups_type(self):
        """Test validation with non-string pushups_type."""
        body = {
            "user_id": "user123",
            "pushups_type": 123,
            "results": {
                "max_push_ups": 50,
                "max_squats": 100,
                "max_reverse_snow_angels_45s": 30,
                "plank_max_time_seconds": 120,
                "mountain_climbers_45s": 80
            }
        }
        is_valid, error = validate_fitness_test_request(body)
        assert is_valid is False
        assert "pushups_type must be a string" in error

    def test_valid_pushups_types(self):
        """Test validation with all valid pushups_type values."""
        valid_types = ["classic", "knee", "incline", "wall"]
        for pushups_type in valid_types:
            body = {
                "user_id": "user123",
                "pushups_type": pushups_type,
                "results": {
                    "max_push_ups": 50,
                    "max_squats": 100,
                    "max_reverse_snow_angels_45s": 30,
                    "plank_max_time_seconds": 120,
                    "mountain_climbers_45s": 80
                }
            }
            is_valid, error = validate_fitness_test_request(body)
            assert is_valid is True
            assert error == ""