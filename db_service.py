import boto3
import logging
from typing import Dict, Any

logger = logging.getLogger()


class DynamoDBService:
    """Service class for DynamoDB operations."""

    def __init__(self, test_results_table: str, user_levels_table: str):
        """
        Initialize DynamoDB service.

        Args:
            test_results_table: Name of the test results DynamoDB table
            user_levels_table: Name of the user levels DynamoDB table
        """
        self.dynamodb = boto3.resource('dynamodb')
        self.test_results_table = self.dynamodb.Table(test_results_table)
        self.user_levels_table = self.dynamodb.Table(user_levels_table)
        self.test_results_table_name = test_results_table
        self.user_levels_table_name = user_levels_table

    def put_test_result(self, item: Dict[str, Any]) -> None:
        """
        Store a test result in DynamoDB.

        Args:
            item: Dictionary containing the test result to store

        Raises:
            Exception: If the put operation fails
        """
        try:
            response = self.test_results_table.put_item(Item=item)
            logger.info(f"Successfully wrote test result to table {self.test_results_table_name}")
            logger.debug(f"DynamoDB response: {response}")
        except Exception as e:
            logger.error(f"Failed to write test result to DynamoDB: {str(e)}")
            raise

    def put_user_level(self, item: Dict[str, Any]) -> None:
        """
        Store user fitness levels in DynamoDB.

        Args:
            item: Dictionary containing the user levels to store

        Raises:
            Exception: If the put operation fails
        """
        try:
            response = self.user_levels_table.put_item(Item=item)
            logger.info(f"Successfully wrote user levels to table {self.user_levels_table_name}")
            logger.debug(f"DynamoDB response: {response}")
        except Exception as e:
            logger.error(f"Failed to write user levels to DynamoDB: {str(e)}")
            raise