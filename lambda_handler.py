import json
import logging
import os
from datetime import datetime
from uuid import uuid4

from db_service import DynamoDBService
from validator import validate_fitness_test_request

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Module-level db_service variable for caching
_db_service = None


def get_db_service():
    """Get or create the DynamoDB service instance."""
    global _db_service
    if _db_service is None:
        table_name = os.environ.get('DYNAMODB_TABLE_NAME', 'test_results')
        _db_service = DynamoDBService(table_name)
    return _db_service


def lambda_handler(event, context):
    """
    AWS Lambda handler for storing fitness test results.

    Expected POST body:
    {
        "user_id": "string",
        "results": {
            "max_push_ups": int,
            "max_squats": int,
            "max_reverse_snow_angels_45s": int,
            "plank_max_time_seconds": int,
            "mountain_climbers_45s": int
        }
    }
    """
    try:
        # Log incoming request
        logger.info(f"Received event: {json.dumps(event)}")

        # Parse request body
        if 'body' not in event:
            logger.error("Missing request body")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing request body'})
            }

        body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']

        # Validate request
        is_valid, error_message = validate_fitness_test_request(body)
        if not is_valid:
            logger.error(f"Validation error: {error_message}")
            return {
                'statusCode': 400,
                'body': json.dumps({'error': error_message})
            }

        # Generate test_id
        test_id = str(uuid4())

        # Prepare item for DynamoDB
        item = {
            'test_id': test_id,
            'user_id': body['user_id'],
            'max_push_ups': body['results']['max_push_ups'],
            'max_squats': body['results']['max_squats'],
            'max_reverse_snow_angels_45s': body['results']['max_reverse_snow_angels_45s'],
            'plank_max_time_seconds': body['results']['plank_max_time_seconds'],
            'mountain_climbers_45s': body['results']['mountain_climbers_45s'],
            'created_at': datetime.utcnow().isoformat()
        }

        # Store in DynamoDB
        db_service = get_db_service()
        db_service.put_item(item)

        # Log success
        logger.info(f"Successfully stored test result with test_id: {test_id}")

        # Return empty 200 OK response
        return {
            'statusCode': 200,
            'body': ''
        }

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON in request body'})
        }

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }