import pytest
import json
import os
from unittest.mock import Mock
from moto import mock_aws
import boto3
from lambda_handler import lambda_handler


class TestLambdaHandler:
    """Tests for the Lambda handler."""

    @pytest.fixture
    def aws_credentials(self):
        """Mock AWS credentials for moto."""
        os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
        os.environ['AWS_SECURITY_TOKEN'] = 'testing'
        os.environ['AWS_SESSION_TOKEN'] = 'testing'
        os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
        os.environ['DYNAMODB_TABLE_NAME'] = 'test-fitness-results'

        # Reset the cached db_service between tests
        import lambda_handler as lh
        lh._db_service = None
        yield
        lh._db_service = None

    @pytest.fixture
    def dynamodb_table(self, aws_credentials):
        """Create a mock DynamoDB table."""
        with mock_aws():
            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
            table = dynamodb.create_table(
                TableName='test-fitness-results',
                KeySchema=[
                    {'AttributeName': 'test_id', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'test_id', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST'
            )
            yield table

    @mock_aws
    def test_successful_request(self, aws_credentials, dynamodb_table):
        """Test a successful fitness test submission."""
        event = {
            'body': json.dumps({
                "user_id": "user123",
                "results": {
                    "max_push_ups": 50,
                    "max_squats": 100,
                    "max_reverse_snow_angels_45s": 30,
                    "plank_max_time_seconds": 120,
                    "mountain_climbers_45s": 80
                }
            })
        }
        context = Mock()

        response = lambda_handler(event, context)

        assert response['statusCode'] == 200
        assert response['body'] == ''

    def test_missing_body(self):
        """Test request without body."""
        event = {}
        context = Mock()

        response = lambda_handler(event, context)

        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body
        assert 'body' in body['error'].lower()

    def test_invalid_json(self):
        """Test request with invalid JSON."""
        event = {
            'body': 'not-valid-json{'
        }
        context = Mock()

        response = lambda_handler(event, context)

        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body
        assert 'JSON' in body['error']

    def test_missing_user_id(self):
        """Test request without user_id."""
        event = {
            'body': json.dumps({
                "results": {
                    "max_push_ups": 50,
                    "max_squats": 100,
                    "max_reverse_snow_angels_45s": 30,
                    "plank_max_time_seconds": 120,
                    "mountain_climbers_45s": 80
                }
            })
        }
        context = Mock()

        response = lambda_handler(event, context)

        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body
        assert 'user_id' in body['error']

    def test_missing_results(self):
        """Test request without results."""
        event = {
            'body': json.dumps({
                "user_id": "user123"
            })
        }
        context = Mock()

        response = lambda_handler(event, context)

        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body
        assert 'results' in body['error']

    def test_missing_exercise_field(self):
        """Test request with missing exercise result."""
        event = {
            'body': json.dumps({
                "user_id": "user123",
                "results": {
                    "max_push_ups": 50,
                    "max_squats": 100,
                    "max_reverse_snow_angels_45s": 30,
                    "plank_max_time_seconds": 120
                    # mountain_climbers_45s is missing
                }
            })
        }
        context = Mock()

        response = lambda_handler(event, context)

        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body
        assert 'mountain_climbers_45s' in body['error']

    def test_negative_exercise_value(self):
        """Test request with negative exercise value."""
        event = {
            'body': json.dumps({
                "user_id": "user123",
                "results": {
                    "max_push_ups": -10,
                    "max_squats": 100,
                    "max_reverse_snow_angels_45s": 30,
                    "plank_max_time_seconds": 120,
                    "mountain_climbers_45s": 80
                }
            })
        }
        context = Mock()

        response = lambda_handler(event, context)

        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body

    @mock_aws
    def test_body_as_dict(self, aws_credentials, dynamodb_table):
        """Test request where body is already a dict (not stringified)."""
        event = {
            'body': {
                "user_id": "user123",
                "results": {
                    "max_push_ups": 50,
                    "max_squats": 100,
                    "max_reverse_snow_angels_45s": 30,
                    "plank_max_time_seconds": 120,
                    "mountain_climbers_45s": 80
                }
            }
        }
        context = Mock()

        response = lambda_handler(event, context)

        assert response['statusCode'] == 200
        assert response['body'] == ''

    @mock_aws
    def test_zero_values(self, aws_credentials, dynamodb_table):
        """Test request with zero values for exercises."""
        event = {
            'body': json.dumps({
                "user_id": "user123",
                "results": {
                    "max_push_ups": 0,
                    "max_squats": 0,
                    "max_reverse_snow_angels_45s": 0,
                    "plank_max_time_seconds": 0,
                    "mountain_climbers_45s": 0
                }
            })
        }
        context = Mock()

        response = lambda_handler(event, context)

        assert response['statusCode'] == 200
        assert response['body'] == ''