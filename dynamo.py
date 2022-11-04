import datetime
import uuid
import json
# 3rd party imports
import boto3
from boto3.dynamodb.conditions import Key, Attr


class Dynamo:
    """DynamoDB functions for lambda

    docs: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html
    """

    def __init__(self, logger):
        """
        args:
            - logger (obj): import logger object using the singleton pattern
        """
        self.client = boto3.resource(
            'dynamodb')
        self.table = None
        self.logger = logger

    def set_table(self, table_name):
        """ Set the table that we want to work with

        args:
            - table_name (str): the table we're writing data to
        """
        self.table = self.client.Table(table_name)

    def dynamo_get_all(self):
        """
        Get all items from the DB.
        """

        self.logger.info('Dynamo.dynamo_get_all: start')

        try:
            # get all items
            items = self.table.scan()
            self.logger.info(f'Dynamo.dynamo_get_all: success')
            return(items.get('Items'))

        except Exception as e:
            # display failure message and return failure status
            self.logger.error(f'Dynamo.dynamo_get_all: failed...\n\n\n {e}')

            return {
                "statusCode": 500,
                "body": json.dumps({"message": "Unable to get items"}),
            }

    def dynamo_filter_by_status(self, status):
        """
        Get all items with the provided status.
        args:
            - status (str): The status we're filtering for
        """

        self.logger.info(f'Dynamo.dynamo_filter_by_status: status {status}')

        try:
            # get all items
            items = self.table.scan(FilterExpression=Attr('status').eq(status))
            self.logger.info(f'Dynamo.dynamo_filter_by_status: success')
            return(items.get('Items'))

        except Exception as e:
            # display failure message and return failure status
            self.logger.error(
                f'Dynamo.dynamo_filter_by_status: failed...\n\n\n {e}')

            return {
                "statusCode": 500,
                "body": json.dumps({"message": "Unable to get approved items"}),
            }

    def dynamo_filter_exclude_status(self, status):
        """
        Get all items without the provided status.
        args:
            - status (str): The status we're filtering for
        """

        self.logger.info(
            f'Dynamo.dynamo_filter_exclude_status: status {status}')

        try:
            # get all items
            items = self.table.scan(FilterExpression=Attr('status').ne(status))
            self.logger.info(f'Dynamo.dynamo_filter_exclude_status: success')
            return(items.get('Items'))

        except Exception as e:
            # display failure message and return failure status
            self.logger.error(
                f'Dynamo.dynamo_filter_exclude_status: failed...\n\n\n {e}')

            return {
                "statusCode": 500,
                "body": json.dumps({"message": "Unable to get approved items"}),
            }

    def dynamo_post(self, data):
        """
        Add a new item to the DB
        args:
            - data (json): the item we're adding to the db
        """

        self.logger.info('Dynamo.dynamo_post: start')

        try:
            item = self.table.put_item(Item=data)
            self.logger.info(f'Dynamo.dynamo_post: success')
            return(item)

        except Exception as e:
            # display failure message and return failure status
            self.logger.error(f'Dynamo.dynamo_post: failed...\n\n\n {e}')

            return {
                "statusCode": 500,
                "body": json.dumps({"message": "Unable to PUT items."}),
            }

    def dynamo_get_item(self, uid):
        """
        get a single item from DynamoDb
        args:
            - uid (str): The ID of the item we're looking for
        """

        self.logger.info('Dynamo.dynamo_get_item: start')

        try:
            item = self.table.get_item(Key={'uid': uid})
            self.logger.info('Dynamo.dynamo_get_item: end.')
            return(item.get('Item'))

        except Exception as e:
            self.logger.error(
                f'Dynamo.dynamo_get_item: Unable to table.get_item() \n\n\n{e}')

            # return empty if error
            # this will allow us to try to save the data
            return {
                "statusCode": 500,
                "body": json.dumps({"message": f"Unable to Get item. ID: {uid}"}),
            }

    def dynamo_put_item(self, data):
        """
        Upload data to DynamoDb
        args:
            - data (json): the data received by the lambda function
        """
        self.logger.info('Dynamo.dynamo_put_item: start')

        # create a new item (row)
        # source: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/dynamodb.html#creating-a-new-item

        try:
            item = self.table.put_item(Item=data)
            self.logger.info(f'Dynamo.dynamo_put_item: success')
            return(item)

        except Exception as e:
            self.logger.error(
                f'Dynamo.dynamo_put_item: dynamodb.table.put_item: {json.dumps(e, indent=4)}')
            return {
                "statusCode": 500,
                "body": json.dumps({"message": "Unable to PUT item."}),
            }

    def dynamo_delete_item(self, uid):
        """
        Upload data to DynamoDb
        args:
            - uid (str): The ID of the item we're looking for
        """
        self.logger.info('Dynamo.dynamo_delete_item: start')

        # create a new item (row)
        # source: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/dynamodb.html#creating-a-new-item

        try:
            item = self.table.delete_item(Key={'uid': uid})
            self.logger.info(f'Dynamo.dynamo_delete_item: success')
            return(item)

        except Exception as e:
            self.logger.error(
                f'Dynamo.dynamo_delete_item: dynamodb.table.put_item: {json.dumps(e, indent=4)}')
            return {
                "statusCode": 500,
                "body": json.dumps({"message": "Unable to DELETE item."}),
            }
