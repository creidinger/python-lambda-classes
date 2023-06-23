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
        self.__logger = logger

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

        self.__logger.info('Dynamo.dynamo_get_all: start')

        try:
            # get all items
            items = self.table.scan()
            self.__logger.info(f'Dynamo.dynamo_get_all: success')
            return (items.get('Items'))

        except Exception as e:
            # display failure message and return failure status
            self.__logger.error(f'Dynamo.dynamo_get_all: failed...\n\n\n {e}')

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

        self.__logger.info(f'Dynamo.dynamo_filter_by_status: status {status}')

        try:
            # get all items
            items = self.table.scan(FilterExpression=Attr('status').eq(status))
            self.__logger.info(f'Dynamo.dynamo_filter_by_status: success')
            return (items.get('Items'))

        except Exception as e:
            # display failure message and return failure status
            self.__logger.error(
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

        self.__logger.info(
            f'Dynamo.dynamo_filter_exclude_status: status {status}')

        try:
            # get all items
            items = self.table.scan(FilterExpression=Attr('status').ne(status))
            self.__logger.info(f'Dynamo.dynamo_filter_exclude_status: success')
            return (items.get('Items'))

        except Exception as e:
            # display failure message and return failure status
            self.__logger.error(
                f'Dynamo.dynamo_filter_exclude_status: failed...\n\n\n {e}')

            return {
                "statusCode": 500,
                "body": json.dumps({"message": "Unable to get active items"}),
            }

    def dynamo_post(self, data):
        """
        Add a new item to the DB
        args:
            - data (json): the item we're adding to the db
        """

        self.__logger.info('Dynamo.dynamo_post: start')

        try:
            item = self.table.put_item(Item=data)
            self.__logger.info(f'Dynamo.dynamo_post: success')
            return (item)

        except Exception as e:
            # display failure message and return failure status
            self.__logger.error(f'Dynamo.dynamo_post: failed...\n\n\n {e}')

            return {
                "statusCode": 500,
                "body": json.dumps({"message": "Unable to POST items."}),
            }

    def dynamo_get_item(self, key_name, key_value):
        """
        get a single item from DynamoDb
        args:
            - key_name (str): The Partition key of the item we're looking for
            - key_value (str): The value of the id we're looking for
        """

        self.__logger.info('Dynamo.dynamo_get_item: start')

        try:
            item = self.table.get_item(Key={key_name: key_value})
            self.__logger.info('Dynamo.dynamo_get_item: end.')
            return (item.get('Item'))

        except Exception as e:
            self.__logger.error(
                f'Dynamo.dynamo_get_item: Unable to table.get_item() \n\n\n{e}')

            # return empty if error
            # this will allow us to try to save the data
            return {
                "statusCode": 500,
                "body": json.dumps({"message": f"Unable to Get item. {key_name}: {key_value}"}),
            }

    def dynamo_put_item(self, data):
        """
        Upload Item to DynamoDb
        args:
            - data (json): the data received by the lambda function
        """
        self.__logger.info('Dynamo.dynamo_put_item: start')

        # create a new item (row)
        # source: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/dynamodb.html#creating-a-new-item

        try:
            item = self.table.put_item(Item=data)
            self.__logger.info(f'Dynamo.dynamo_put_item: success')
            return (item)

        except Exception as e:
            self.__logger.error(
                f'Dynamo.dynamo_put_item: dynamodb.table.put_item: \n\n\n{e}')
            return {
                "statusCode": 500,
                "body": json.dumps({"message": "Unable to PUT item."}),
            }

    def dynamo_delete_item(self, key_name, key_value):
        """
        Delete Item from DynamoDb
        args:
            - key (str): The ID of the item we're looking for
        """
        self.__logger.info('Dynamo.dynamo_delete_item: start')

        # create a new item (row)
        # source: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/dynamodb.html#creating-a-new-item

        try:
            item = self.table.delete_item(Key={key_name: key_value})
            self.__logger.info(f'Dynamo.dynamo_delete_item: success')
            return (item)

        except Exception as e:
            self.__logger.error(
                f'Dynamo.dynamo_delete_item: table.delete_item: \n\n\n{e}')
            return {
                "statusCode": 500,
                "body": json.dumps({"message": "Unable to DELETE item."}),
            }

    def dynamo_search(self, prefix, key_name, limit, last_key):
        """
        Searches for items in a DynamoDB table based on a prefix and key.

        Args:
            prefix (str): The prefix to search for.
            key (str): The key to filter the search on.
            limit (number): The number of items we want to return
            last_key (str): The key of the last item in the list that we previously returned

        Docs: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/scan.html
        """

        self.__logger.info('Dynamo.dynamo_search: start')

        searchFilter = {
            'TableName': self.table.table_name,
            'FilterExpression': f'begins_with({key_name}, :prefix)',
            'ExpressionAttributeValues': {
                ':prefix': prefix,
            },
        }

        # todo: Revisit Pagintaion
        #  searchFilter = {
        #     'TableName': self.table.table_name,
        #     'FilterExpression': f'begins_with({key}, :prefix)',
        #     'ExpressionAttributeValues': {
        #         ':prefix': prefix,
        #     },
        #     'Limit': int(limit),
        # }

        # # When a start key is provided
        # # add it to the search filter
        # if last_key and last_key is not "":
        #     searchFilter["ExclusiveStartKey"] = {'uid': last_key}

        try:
            response = self.table.scan(**searchFilter)
        except Exception as e:
            self.__logger.error(f'Dynamo.dynamo_search: {str(e)}')
            return {
                "statusCode": 500,
                "body": json.dumps({"message": "Unable to search for items."}),
            }

        self.__logger.info('Dynamo.dynamo_search: success')

        return response

    def dynamo_search_duplicate(self, key_name, key_value):
        """
        Searches for an existing item in a DynamoDB table

        Args:
            key (str): The key to filter the search on.
            value (str): The prefix to search for.

        Docs: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/scan.html
        """

        self.__logger.info('Dynamo.dynamo_search_duplicate: start')

        try:
            response = self.table.scan(
                FilterExpression=Attr(key_name).eq(key_value))
        except Exception as e:
            self.__logger.error(f'Dynamo.dynamo_search_duplicate: {str(e)}')
            return {
                "statusCode": 500,
                "body": json.dumps({"message": "Unable to search for items."}),
            }

        self.__logger.info('Dynamo.dynamo_search_duplicate: success')

        return response
