import datetime
import uuid
# 3rd party imports
import boto3
from boto3.dynamodb.conditions import Key


class Dynamo:
    """DynamoDB functions for lambda"""

    def __init__(self, settings, logger):
        """
        args:
            - settings (obj): import settings using the singleton pattern
            - logger (obj): import logger object using the singleton pattern
        """
        self.dynamodb = boto3.resource(
            'dynamodb')    # The type of client we're using
        self.prod_table_name = settings.dynamodb_table
        self.staging_table_name = settings.dynamodb_table_staging
        self.logger = logger

    def dynamo_get_active_table(self, use_production):
        """ Determine which environment to use
        args:
            - use_production (bool): Tells which environment we're working in
        """
        # determine which env to store data
        if use_production:
            return self.prod_table_name

        return self.staging_table_name

    def dynamo_get(self, data, use_production):
        """
        get and item from DynamoDb
        args:
            - data (json): the data received by the lambda function
            - use_production (bool): Tells which environment we're working in
        """
        self.logger.info('Dynamo.dynamo_get: Checking if the user exists.')

        # get the table and init
        active_table = self.dynamo_get_active_table(
            use_production=use_production)
        table = self.dynamodb.Table(active_table)
        item = None

        try:
            response = table.get_item(
                Key={
                    'email': data['email'],
                }
            )
        except Exception as e:
            self.logger.error('Dynamo.dynamo_get: Unable to table.get_item()')
            self.logger.error(f'Dynamo.dynamo_get: {e}')
            # return empty if error
            # this will allow us to try to save the data
            return item

        item = response["Item"]
        self.logger.info('Dynamo.dynamo_get: end.')
        return item

    def dynamo_update_item(self, data, use_production):
        """
        Update an existing user DynamoDb
        args:
            - data (json): the data received by the lambda function
            - use_production (bool): Tells which environment we're working in
        """

        self.logger.info(
            'Dynamo.dynamo_update_item: dynamodb.table.update_item: Start.')
        # get the table and init
        active_table = self.dynamo_get_active_table(
            use_production=use_production)
        table = self.dynamodb.Table(active_table)

        try:
            table.update_item(
                Key={
                    'email': data['email']
                },
                UpdateExpression="set #contact_name=:n, phone=:p, email=:e, messsage=:m, edit_date=:d",
                ExpressionAttributeValues={
                    ':n': data["name"],
                    ':p': data["phone"],
                    ':e': data["email"],
                    ':m': data["message"],
                    ':d': str(datetime.datetime.now())
                },
                # Doc below explains how to handle updating a table
                # that contains a reserved name
                # https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Expressions.ExpressionAttributeNames.html
                ExpressionAttributeNames={
                    "#contact_name": "name"
                }
            )
        except Exception as e:
            self.logger.info(
                'Dynamo.dynamo_update_item: dynamodb.table.update_item: end.')
            self.logger.error(
                f'Dynamo.dynamo_update_item: dynamodb.table.update_item: {e}')
            return False
        else:
            self.logger.info(
                'Dynamo.dynamo_update_item: dynamodb.table.update_item: Success!!!')
            return True

    def dynamo_put(self, data, use_production):
        """
        Upload data to DynamoDb
        args:
            - data (json): the data received by the lambda function
            - use_production (bool): Tells which environment we're working in
        """
        self.logger.info(
            'Dynamo.dynamo_put: uploading event data to DynamoDb...')

        # get the table and init
        active_table = self.dynamo_get_active_table(
            use_production=use_production)
        table = self.dynamodb.Table(active_table)

        # create a new item (row)
        # source: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/dynamodb.html#creating-a-new-item

        try:
            table.put_item(
                Item={
                    # generate a ramdom/unique ID for each DB Entry
                    'id': str(uuid.uuid4()),
                    'name': data['name'],
                    'phone': data['phone'],
                    'email': data['email'],
                    'message': data['message'],
                    'create_date': str(datetime.datetime.now()),
                    'edit_date': None,
                }
            )
        except Exception as e:
            self.logger.error(
                f'Dynamo.dynamo_put: dynamodb.table.put_item: {e}')
            return False
        else:
            self.logger.info(
                'Dynamo.dynamo_put: dynamodb.table.put_item: Success!!!')
            return True
