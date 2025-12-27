import pytest
from moto import mock_aws
import boto3
from decimal import Decimal
from db_service import DynamoDBService


class TestDynamoDBService:
    """Tests for the DynamoDB service."""

    @pytest.fixture
    def aws_credentials(self):
        """Mock AWS credentials for moto."""
        import os
        os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
        os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
        os.environ['AWS_SECURITY_TOKEN'] = 'testing'
        os.environ['AWS_SESSION_TOKEN'] = 'testing'
        os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

    @pytest.fixture
    def dynamodb_tables(self, aws_credentials):
        """Create mock DynamoDB tables."""
        with mock_aws():
            dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

            # Create test_results table
            test_results_table = dynamodb.create_table(
                TableName='test-fitness-results',
                KeySchema=[
                    {'AttributeName': 'test_id', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'test_id', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST'
            )

            # Create user_levels table
            user_levels_table = dynamodb.create_table(
                TableName='test-user-levels',
                KeySchema=[
                    {'AttributeName': 'user_level_id', 'KeyType': 'HASH'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'user_level_id', 'AttributeType': 'S'}
                ],
                BillingMode='PAY_PER_REQUEST'
            )

            yield {
                'test_results': test_results_table,
                'user_levels': user_levels_table
            }

    @pytest.fixture
    def db_service(self, dynamodb_tables):
        """Create a DynamoDB service instance."""
        return DynamoDBService('test-fitness-results', 'test-user-levels')

    @mock_aws
    def test_put_test_result_success(self, aws_credentials, db_service, dynamodb_tables):
        """Test successfully storing a test result in DynamoDB."""
        item = {
            'test_id': 'test-123',
            'user_id': 'user-456',
            'pushups_type': 'classic',
            'max_push_ups': 50,
            'max_squats': 100,
            'max_reverse_snow_angels_45s': 30,
            'plank_max_time_seconds': 120,
            'mountain_climbers_45s': 80,
            'created_at': '2025-12-22T10:30:00.123456'
        }

        # Should not raise any exceptions
        db_service.put_test_result(item)

        # Verify the item was stored
        response = dynamodb_tables['test_results'].get_item(Key={'test_id': 'test-123'})
        assert 'Item' in response
        assert response['Item']['user_id'] == 'user-456'
        assert response['Item']['max_push_ups'] == 50

    @mock_aws
    def test_put_test_result_with_all_fields(self, aws_credentials, db_service, dynamodb_tables):
        """Test storing a test result with all expected fields."""
        item = {
            'test_id': 'test-789',
            'user_id': 'user-999',
            'pushups_type': 'knee',
            'max_push_ups': 25,
            'max_squats': 75,
            'max_reverse_snow_angels_45s': 20,
            'plank_max_time_seconds': 90,
            'mountain_climbers_45s': 60,
            'created_at': '2025-12-22T15:45:00.123456'
        }

        db_service.put_test_result(item)

        # Verify all fields were stored
        response = dynamodb_tables['test_results'].get_item(Key={'test_id': 'test-789'})
        stored_item = response['Item']
        assert stored_item['test_id'] == 'test-789'
        assert stored_item['user_id'] == 'user-999'
        assert stored_item['pushups_type'] == 'knee'
        assert stored_item['created_at'] == '2025-12-22T15:45:00.123456'

    @mock_aws
    def test_put_user_level_success(self, aws_credentials, db_service, dynamodb_tables):
        """Test successfully storing user levels in DynamoDB."""
        item = {
            'user_level_id': 'level-123',
            'user_id': 'user-456',
            'test_id': 'test-789',
            'per_category': {
                'LOWER': 'INTERMEDIATE',
                'PUSH': 'ADVANCED',
                'PULL': 'BEGINNER',
                'CORE': 'INTERMEDIATE',
                'COND': 'INTERMEDIATE'
            },
            'global_level': 'INTERMEDIATE',
            'global_level_raw_avg_points': Decimal('2.0'),  # Use Decimal for DynamoDB
            'created_at': '2025-12-22T10:30:00.123456'
        }

        # Should not raise any exceptions
        db_service.put_user_level(item)

        # Verify the item was stored
        response = dynamodb_tables['user_levels'].get_item(Key={'user_level_id': 'level-123'})
        assert 'Item' in response
        assert response['Item']['user_id'] == 'user-456'
        assert response['Item']['test_id'] == 'test-789'
        assert response['Item']['global_level'] == 'INTERMEDIATE'
        assert response['Item']['per_category']['PUSH'] == 'ADVANCED'
        assert response['Item']['global_level_raw_avg_points'] == Decimal('2.0')