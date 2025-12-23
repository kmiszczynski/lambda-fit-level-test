import boto3
import logging
from typing import Dict, Any

logger = logging.getLogger()


class DynamoDBService:
    """Service class for DynamoDB operations."""

    def __init__(self, table_name: str):
        """
        Initialize DynamoDB service.

        Args:
            table_name: Name of the DynamoDB table
        """
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)
        self.table_name = table_name

    def put_item(self, item: Dict[str, Any]) -> None:
        """
        Store an item in DynamoDB.

        Args:
            item: Dictionary containing the item to store

        Raises:
            Exception: If the put operation fails
        """
        try:
            response = self.table.put_item(Item=item)
            logger.info(f"Successfully wrote item to table {self.table_name}")
            logger.debug(f"DynamoDB response: {response}")
        except Exception as e:
            logger.error(f"Failed to write item to DynamoDB: {str(e)}")
            raise