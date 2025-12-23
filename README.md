# Fitness Level Test - AWS Lambda Function

AWS Lambda function for storing fitness test results in DynamoDB.

## Overview

This Lambda function handles POST requests from API Gateway to store fitness test results. It validates incoming data, generates unique test IDs, and persists results to DynamoDB.

## Project Structure

```
.
├── lambda_handler.py          # Main Lambda entry point
├── db_service.py              # DynamoDB service layer
├── validator.py               # Request validation logic
├── requirements.txt           # Python dependencies
├── tests/                     # Test suite
│   ├── test_lambda_handler.py
│   ├── test_db_service.py
│   └── test_validator.py
├── CLAUDE.md                  # Claude Code documentation
└── README.md                  # This file
```

## Quick Start

### Install Dependencies

```bash
# Activate virtual environment
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=term-missing
```

### Deploy to AWS Lambda

```bash
# Package the function
pip install -r requirements.txt -t package/
cp lambda_handler.py db_service.py validator.py package/
cd package && zip -r ../lambda_function.zip . && cd ..

# Upload lambda_function.zip to AWS Lambda
```

## Environment Variables

- `DYNAMODB_TABLE_NAME`: DynamoDB table name (default: 'test_results')

## API Request Format

**Endpoint**: POST /fitness-test

**Request Body**:
```json
{
    "user_id": "user123",
    "results": {
        "max_push_ups": 50,
        "max_squats": 100,
        "max_reverse_snow_angels_45s": 30,
        "plank_max_time_seconds": 120,
        "mountain_climbers_45s": 80
    }
}
```

**Success Response**: HTTP 200 (empty body)

**Error Response**: HTTP 400 or 500 with error details

## DynamoDB Table Schema

**Table Name**: `test_results`

**Primary Key**: `test_id` (String)

**Attributes**:
- `test_id`: UUID4 (auto-generated)
- `user_id`: String
- `max_push_ups`: Number
- `max_squats`: Number
- `max_reverse_snow_angels_45s`: Number
- `plank_max_time_seconds`: Number
- `mountain_climbers_45s`: Number
- `created_at`: ISO 8601 timestamp (auto-generated)

## Testing

The project includes comprehensive test coverage:
- **19 tests** covering all validation scenarios, database operations, and Lambda handler logic
- Uses `moto` for mocking AWS services
- All tests passing ✓

## AWS Lambda Configuration

- **Runtime**: Python 3.9+
- **Handler**: `lambda_handler.lambda_handler`
- **Memory**: 128 MB (recommended minimum)
- **Timeout**: 30 seconds (recommended)
- **IAM Permissions**: `dynamodb:PutItem` on the target table