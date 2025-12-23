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
cp lambda_handler.py db_service.py validator.py package/
cd package && zip -r ../lambda_function.zip . && cd ..
```

## Code Architecture

### Module Structure

**lambda_handler.py**: Main Lambda entry point
- `lambda_handler(event, context)`: Handles incoming API Gateway POST requests
- Parses and validates request body
- Generates UUID for test_id
- Stores data in DynamoDB
- Returns 200 OK on success, 400 for validation errors, 500 for server errors
- Logs all requests, responses, and errors

**db_service.py**: DynamoDB data access layer
- `DynamoDBService`: Class for DynamoDB operations
- `put_item(item)`: Stores fitness test results in DynamoDB
- Handles boto3 DynamoDB resource and table operations

**validator.py**: Request validation logic
- `validate_fitness_test_request(body)`: Validates incoming request structure
- Checks for required fields: user_id, results
- Validates data types (strings, integers)
- Ensures all exercise results are non-negative integers
- Returns tuple of (is_valid: bool, error_message: str)

### Data Model

**DynamoDB Item Structure**:
```python
{
    'test_id': 'uuid4-string',           # Primary key, auto-generated
    'user_id': 'string',                 # Required
    'max_push_ups': int,                 # Required, >= 0
    'max_squats': int,                   # Required, >= 0
    'max_reverse_snow_angels_45s': int,  # Required, >= 0
    'plank_max_time_seconds': int,       # Required, >= 0
    'mountain_climbers_45s': int,        # Required, >= 0
    'created_at': 'ISO 8601 string'      # Auto-generated
}
```

**Expected API Request Format**:
```json
{
    "user_id": "string",
    "results": {
        "max_push_ups": 50,
        "max_squats": 100,
        "max_reverse_snow_angels_45s": 30,
        "plank_max_time_seconds": 120,
        "mountain_climbers_45s": 80
    }
}
```

### Environment Variables

- `DYNAMODB_TABLE_NAME`: Name of the DynamoDB table (default: 'test_results')

### Testing Strategy

Tests use `moto` for mocking AWS services and `pytest` for test execution. Each module has comprehensive test coverage:
- **test_validator.py**: Tests all validation scenarios
- **test_db_service.py**: Tests DynamoDB operations with mocked AWS
- **test_lambda_handler.py**: Integration tests for the full Lambda handler

### AWS Lambda Configuration

The Lambda function expects:
- Runtime: Python 3.9+
- Handler: `lambda_handler.lambda_handler`
- IAM Role with permissions: `dynamodb:PutItem`
- Environment variable: `DYNAMODB_TABLE_NAME`
- Trigger: API Gateway POST endpoint