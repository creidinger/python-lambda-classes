import os
# 3rd part imports
import boto3


class SimpleEmailService:
    """AWS Simple Email Service functions for lambda

    docs: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ses.html
    """

    def __init__(self, logger):
        """

        Args:
            region_name (str): The AWS region we're using
            logger (obj): import logger object using the singleton pattern
        """
        self.region_name = "us-east-1"  # default value
        self.charset = 'UTF-8'  # default value
        self.client = boto3.client("ses", region_name=self.region_name)
        self.__logger = logger
        self.receiver = os.environ["email_receiver_dev"]
        self.email_subject = os.environ["email_subject_test"]
        self.email_from_name = os.environ["email_from_name"]
        self.sender = os.environ["email_sender"]

    def set_region(self, region_name):
        """Set the region we will be using to send emails

        Args:
            region_name (str): The region we want to change too
        """

        self.__logger.info('SimpleEmailService.set_region: start')

        self.region_name = region_name

        self.__logger.info(
            f'SimpleEmailService.set_region: end - using region {self.region_name}')

    def set_charset(self, charset):
        """set the charset that the email will use while sending

        Args:
            charset (str): The charset that will be used to send the email
        """
        self.__logger.info('SimpleEmailService.set_charset: start')

        self.charset = charset

        self.__logger.info(
            f'SimpleEmailService.set_charset: end - using charset {self.charset}')

    def set_email_meta(self, stage):
        """Checks the environment to determine the emails receiver and subject

        Args:
            stage (str): the API environemnt we're using to detect dev, staging, and prod.
        """

        self.__logger.info("SimpleEmailService.set_email_meta: start...")

        self.__logger.info(
            f'SimpleEmailService.set_email_meta: Dev Env is default.')

        self.__logger.info(
            f'SimpleEmailService.set_email_meta: Checking staging or production')

        # determine which person to send the email to
        if stage == "v1":
            self.__logger.info(
                f'SimpleEmailService.set_email_meta: Using Prod')
            self.receiver = os.environ["email_receiver_prod"]
            self.email_subject = os.environ["email_subject_prod"]

        if stage == "stage":
            self.__logger.info(
                f'SimpleEmailService.set_email_meta: Using staging')
            self.receiver = os.environ["email_receiver_staging"]
            self.email_subject = os.environ["email_subject_test"]

        self.__logger.info(
            f'SimpleEmailService.set_email_meta: receiver: {self.receiver}')
        self.__logger.info(
            f'SimpleEmailService.set_email_meta: email_subject: {self.email_subject}')

        self.__logger.info("SimpleEmailService.set_email_meta: end...")

    def send_email(self, message_body):
        """Send email to client and information of a

        AWS Boto3 docs: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ses.html

        Args:
            message_body(str): The body of the email that will be sent
        """
        self.__logger.info("SimpleEmailService.send_email: start")

        try:
            # send email
            response = self.client.send_email(
                Destination={
                    "ToAddresses": [
                        self.receiver,
                    ],
                },
                Message={
                    "Body": {
                        "Html": {
                            "Charset": self.charset,
                            "Data": message_body,
                        }
                    },
                    "Subject": {
                        "Charset": self.charset,
                        "Data": self.email_subject,
                    },
                },
                Source=f'{self.email_from_name} <{self.sender}>',
            )
            self.__logger.info("SimpleEmailService.send_email: success!")

        except Exception as e:
            self.__logger.error(
                "SimpleEmailService.send_email: unable to send eamil")
            self.__logger.error(f"SimpleEmailService.send_email: {e}")
            return False

        self.__logger.info("SimpleEmailService.send_email: end")
        return True
