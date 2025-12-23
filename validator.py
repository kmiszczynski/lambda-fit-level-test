from typing import Tuple


def validate_fitness_test_request(body: dict) -> Tuple[bool, str]:
    """
    Validate the fitness test request body.

    Args:
        body: Request body dictionary

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check required top-level fields
    if 'user_id' not in body:
        return False, "Missing required field: user_id"

    if 'results' not in body:
        return False, "Missing required field: results"

    # Validate user_id
    if not isinstance(body['user_id'], str) or not body['user_id'].strip():
        return False, "user_id must be a non-empty string"

    # Validate results object
    results = body['results']
    if not isinstance(results, dict):
        return False, "results must be an object"

    # Required result fields
    required_fields = [
        'max_push_ups',
        'max_squats',
        'max_reverse_snow_angels_45s',
        'plank_max_time_seconds',
        'mountain_climbers_45s'
    ]

    for field in required_fields:
        if field not in results:
            return False, f"Missing required result field: {field}"

        value = results[field]
        if not isinstance(value, int):
            return False, f"{field} must be an integer"

        if value < 0:
            return False, f"{field} must be non-negative"

    return True, ""