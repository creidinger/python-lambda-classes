import os
# 3rd part imports
import boto3
from botocore.exceptions import ClientError


class S3:
    """AWS Simple Email Service functions for lambda

    docs: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html
    """

    def __init__(self, logger):
        """

        Args:
            - logger (obj): import logger object using the singleton pattern
        """
        self.__logger = logger
        self.region_name = "us-east-1"  # default value
        self.client = None

    def set_region(self, region_name):
        """Set the region we will be using to send emails

        Args:
            - region_name (str): The region we want to change too
        """

        self.__logger.info('S3.set_region: start')

        self.region_name = region_name

        self.__logger.info(
            f'S3.set_region: end - using region {self.region_name}')

    def set_s3_client(self, ACCESS_KEY, SECRET):
        """Init the s3 client

        Args:
            ACCESS_KEY (str): The access key for this bucket
            SECRET (str): The secret key for this bucket
        """

        self.__logger.info('S3.set_s3_client: start')

        try:
            self.client = boto3.client(
                's3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET)

        except Exception as e:
            self.__logger.error(f'S3.set_s3_client: {e}')

        self.__logger.info('S3.set_s3_client: end')

    def upload_to_butcket(self, file_name, bucket, object_name):
        """Upload an object to a bucket
        source: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-uploading-files.html


        Args:
            - file_name (str): The file we're uploading
                Ex: my_file.pdf
            - bucket (str): Bucket to upload to
            - object_name (str): S3 object name.
        """

        self.__logger.info("S3.upload_to_butcket: start...")

        try:
            response = self.client.upload_file(file_name, bucket, object_name)

        except ClientError as e:
            self.__logger.error(
                f'upload_to_s3: S3 upload failed \n{e}')
            self.__logger.error('upload_to_s3: Exit')
            return False

        self.__logger.info("S3.upload_to_butcket: Success - end...")
        return True
