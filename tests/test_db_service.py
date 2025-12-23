import pytest
from moto import mock_aws
import boto3
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

    @pytest.fixture
    def db_service(self, dynamodb_table):
        """Create a DynamoDB service instance."""
        return DynamoDBService('test-fitness-results')

    @mock_aws
    def test_put_item_success(self, aws_credentials, db_service, dynamodb_table):
        """Test successfully storing an item in DynamoDB."""
        item = {
            'test_id': 'test-123',
            'user_id': 'user-456',
            'max_push_ups': 50,
            'max_squats': 100,
            'max_reverse_snow_angels_45s': 30,
            'plank_max_time_seconds': 120,
            'mountain_climbers_45s': 80,
            'created_at': '2025-12-22T10:30:00.123456'
        }

        # Should not raise any exceptions
        db_service.put_item(item)

        # Verify the item was stored
        response = dynamodb_table.get_item(Key={'test_id': 'test-123'})
        assert 'Item' in response
        assert response['Item']['user_id'] == 'user-456'
        assert response['Item']['max_push_ups'] == 50

    @mock_aws
    def test_put_item_with_all_fields(self, aws_credentials, db_service, dynamodb_table):
        """Test storing an item with all expected fields."""
        item = {
            'test_id': 'test-789',
            'user_id': 'user-999',
            'max_push_ups': 25,
            'max_squats': 75,
            'max_reverse_snow_angels_45s': 20,
            'plank_max_time_seconds': 90,
            'mountain_climbers_45s': 60,
            'created_at': '2025-12-22T15:45:00.123456'
        }

        db_service.put_item(item)

        # Verify all fields were stored
        response = dynamodb_table.get_item(Key={'test_id': 'test-789'})
        stored_item = response['Item']
        assert stored_item['test_id'] == 'test-789'
        assert stored_item['user_id'] == 'user-999'
        assert stored_item['created_at'] == '2025-12-22T15:45:00.123456'