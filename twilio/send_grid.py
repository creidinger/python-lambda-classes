import os
import json
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


class SendGrid():
    """Sendgrid api integration

    using SendGrid's Python Library: https://github.com/sendgrid/sendgrid-python
    source: https://sendgrid.com/solutions/email-api/
    """

    def __init__(self, logger, from_email, to_emails):
        """

        Args:
            - logger (obj): import logger object using the singleton pattern
            - from_email (str): The email of address of the sender
            - to_emails (str): a comma separated list of email addresses
        """

        self.__logger = logger
        self.from_email = from_email
        self.to_emails = to_emails

    def set_email_sender(self, email_address):
        """Set the email send address

        Args:
            email_address (str): The email of address of the sender
        """

        self.__logger.info("SendGrid.set_email_sender: start")

        try:
            self.from_email = email_address
            self.__logger.info("SendGrid.set_email_sender: success")

        except Exception as e:
            self.__logger.error(f"SendGrid.set_email_sender: {e}")
            return {
                "statusCode": 500,
                "body": json.dumps({"message": "Unable to set sender email"}),
            }

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "success"}),
        }

    def set_email_receivers(self, email_addresses):
        """Se the email address that will be receiving emails

        Args:
            email_addresses (str): a comma separated list of email addresses
        """

        self.__logger.info("SendGrid.set_email_receivers: start")

        try:
            self.to_emails = email_addresses
            self.__logger.info("SendGrid.set_email_receivers: success")

        except Exception as e:
            self.__logger.error(f"SendGrid.set_email_receivers: {e}")
            return {
                "statusCode": 500,
                "body": json.dumps({"message": "Unable to set email receivers"}),
            }

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "success"}),
        }

    def send_email(self, subject, message_body):
        """Send an email using the Sendgrid API

        Args:
            subject (str): The subject of the email we're looking to send
            message_body (str): The email message we're looking to send
        """

        self.__logger.info("SendGrid.send_email: start")

        # create mail object
        message = Mail(
            from_email=self.from_email,
            to_emails=self.to_emails,
            subject=subject,
            html_content=message_body)

        try:
            # try to send email
            sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
            response = sg.send(message)
            self.__logger.info(
                f"SendGrid.send_email - response.status_code: {response.status_code}")
            self.__logger.info(
                f"SendGrid.send_email - response.body: {response.body}")
            self.__logger.info(
                f"SendGrid.send_email - response.headers: {response.headers}")

        except Exception as e:
            self.__logger.error(f"SendGrid.send_email: {e}")
            return {
                "statusCode": 500,
                "body": json.dumps({"message": "Unable to send email"}),
            }

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "success"}),
        }
