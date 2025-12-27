# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based AWS Lambda function project for fitness level testing. 
This lambda will handle POST api request to store results of fitness test in dynamoDB.

Test result will include results from 5 exercises:
- maximum push-ups
- maximum squats
- maximum reverse snow angels in 45s
- plank (max time)
- mountain climbers in 45s

We will also store test_id (generated uuid4), user_id (string) and created_at timestamp (auto-generated ISO 8601 string).
In the response we should return empty 200 OK response when everything is good.

Requests and responses should be logged. Errors should be logged also.

## Development Environment

**Virtual Environment**: `.venv` directory contains the Python virtual environment.

### Activating the Virtual Environment

Windows:
```bash
.venv\Scripts\activate
```

Linux/macOS:
```bash
source .venv/bin/activate
```

## Common Commands

### Dependency Management
```bash
# Install dependencies (when requirements.txt exists)
pip install -r requirements.txt

# Freeze current dependencies
pip freeze > requirements.txt
```

### Testing
```bash
# Run all tests
pytest

# Run a specific test file
pytest tests/test_validator.py
pytest tests/test_db_service.py
pytest tests/test_lambda_handler.py

# Run tests with coverage
pytest --cov=. --cov-report=term-missing

# Run tests excluding the virtual environment
pytest --ignore=.venv
```

### Lambda Deployment

```bash
# Package Lambda function for deployment
pip install -r requirements.txt -t package/
cp lambda_handler.py db_service.py validator.py level_calculator.py package/
cd package && zip -r ../lambda_function.zip . && cd ..
```

**Important**: Make sure to include ALL Python modules:
- `lambda_handler.py` - Main Lambda entry point
- `db_service.py` - DynamoDB service layer
- `validator.py` - Request validation
- `level_calculator.py` - Fitness level calculation logic

## Code Architecture

### Module Structure

**lambda_handler.py**: Main Lambda entry point
- `lambda_handler(event, context)`: Handles incoming API Gateway POST requests
- Parses and validates request body
- Generates UUIDs for test_id and user_level_id
- Calculates fitness levels using level_calculator
- Stores test results in test_results table
- Stores calculated levels in user_levels table
- Returns 200 with calculated levels JSON on success, 400 for validation errors, 500 for server errors
- Logs all requests, responses, and errors

**db_service.py**: DynamoDB data access layer
- `DynamoDBService`: Class for DynamoDB operations with two tables
- `put_test_result(item)`: Stores fitness test results in test_results table
- `put_user_level(item)`: Stores calculated fitness levels in user_levels table
- Handles boto3 DynamoDB resource and table operations

**validator.py**: Request validation logic
- `validate_fitness_test_request(body)`: Validates incoming request structure
- Checks for required fields: user_id, pushups_type, results
- Validates data types (strings, integers)
- Ensures all exercise results are non-negative integers
- Validates pushups_type is one of: classic, knee, incline, wall
- Returns tuple of (is_valid: bool, error_message: str)

**level_calculator.py**: Fitness level calculation logic
- `TestResults`: Dataclass matching DynamoDB structure
- `compute_levels(results)`: Calculates fitness levels for all categories
- Individual level functions: level_lower_from_squats, level_push_from_pushups, etc.
- Returns per-category levels and global fitness level
- Includes corrective rule: BEGINNER + ADVANCED caps global to INTERMEDIATE

### Data Model

**test_results Table Structure**:
```python
{
    'test_id': 'uuid4-string',           # Primary key, auto-generated
    'user_id': 'string',                 # Required
    'pushups_type': 'string',            # Required: classic, knee, incline, wall
    'max_push_ups': int,                 # Required, >= 0
    'max_squats': int,                   # Required, >= 0
    'max_reverse_snow_angels_45s': int,  # Required, >= 0
    'plank_max_time_seconds': int,       # Required, >= 0
    'mountain_climbers_45s': int,        # Required, >= 0
    'created_at': 'ISO 8601 string'      # Auto-generated
}
```

**user_levels Table Structure**:
```python
{
    'user_level_id': 'uuid4-string',     # Primary key, auto-generated
    'user_id': 'string',                 # Reference to user
    'test_id': 'string',                 # Reference to test_results
    'per_category': {
        'LOWER': 'BEGINNER|INTERMEDIATE|ADVANCED',
        'PUSH': 'BEGINNER|INTERMEDIATE|ADVANCED',
        'PULL': 'BEGINNER|INTERMEDIATE|ADVANCED',
        'CORE': 'BEGINNER|INTERMEDIATE|ADVANCED',
        'COND': 'BEGINNER|INTERMEDIATE|ADVANCED'
    },
    'global_level': 'BEGINNER|INTERMEDIATE|ADVANCED',
    'global_level_raw_avg_points': Decimal,  # Average points (1-3)
    'created_at': 'ISO 8601 string'      # Auto-generated
}
```

**Expected API Request Format**:
```json
{
    "user_id": "string",
    "pushups_type": "classic",
    "results": {
        "max_push_ups": 50,
        "max_squats": 100,
        "max_reverse_snow_angels_45s": 30,
        "plank_max_time_seconds": 120,
        "mountain_climbers_45s": 80
    }
}
```

**API Response Format**:
```json
{
    "user_level_id": "uuid-string",
    "test_id": "uuid-string",
    "levels": {
        "per_category": {
            "LOWER": "ADVANCED",
            "PUSH": "ADVANCED",
            "PULL": "INTERMEDIATE",
            "CORE": "ADVANCED",
            "COND": "ADVANCED"
        },
        "global_level": "ADVANCED",
        "global_level_raw_avg_points": 2.8
    }
}
```

### Environment Variables

- `DYNAMODB_TABLE_NAME`: Name of the test results DynamoDB table (default: 'test_results')
- `USER_LEVELS_TABLE_NAME`: Name of the user levels DynamoDB table (default: 'user_levels')

### Testing Strategy

Tests use `moto` for mocking AWS services and `pytest` for test execution. Each module has comprehensive test coverage:
- **test_validator.py**: Tests all validation scenarios including pushups_type validation
- **test_db_service.py**: Tests DynamoDB operations for both tables with mocked AWS
- **test_lambda_handler.py**: Integration tests for the full Lambda handler including level calculation
- **test_level_calculator.py**: Tests for fitness level calculation logic and all category functions

### AWS Lambda Configuration

The Lambda function expects:
- Runtime: Python 3.9+
- Handler: `lambda_handler.lambda_handler`
- IAM Role with permissions: `dynamodb:PutItem` on both tables
- Environment variables:
  - `DYNAMODB_TABLE_NAME` (test results table)
  - `USER_LEVELS_TABLE_NAME` (user levels table)
- Trigger: API Gateway POST endpoint

**Required DynamoDB Tables**:
1. **test_results** table with primary key: `test_id` (String)
2. **user_levels** table with primary key: `user_level_id` (String)