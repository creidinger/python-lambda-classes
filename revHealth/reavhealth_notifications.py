import os
# 3rd party
import requests


class Notifications():
    """This class sends notifications the RH api which are then passed to Ms Teams"""

    def __init__(self, endpoint, logger, event):
        """
        Args:
            endpoint (_type_): The API endpoint we're posting notificaitons too
            logger (obj): import logger object using the singleton pattern
            event (json): Event data that has trigged the lambda function
        """

        # private vars
        self.__logger = logger
        self.__event = event
        self.endpoint = endpoint
        self.payload = None

    def send_notification(self, failed_function_name, description):
        """Send a POST request to the RH API

        Args:
            function_name (str): The name of the fucntion that failed within lambda
            description (str): A scrption of the potentail problem
        """

        self.__logger.info("Notifications.send_notification: start")

        headers = {
            "contentType": "application/json"
        }

        self.set_payload(failed_function_name, description)

        try:
            r = requests.post(self.endpoint, headers=headers,
                              json=self.payload)

        except Exception as e:
            self.__logger.error("Notifications.send_notification: failed!!!")
            self.__logger.error(f"Notifications.send_notification: {e}")

        self.__logger.info("Notifications.send_notification: end")
        return True

    def set_payload(self, failed_function_name, description):
        """Build the payload that will be sent to teams

        Args:
            function_name (str): The name of the fucntion that failed within lambda
            description (str): A scrption of the potentail problem
        """

        self.__logger.info("Notifications.set_payload: start")

        # build the base payload
        self.payload = {
            "lambda_name": os.environ["AWS_LAMBDA_FUNCTION_NAME"],
            "function_name": failed_function_name,
            "description": description,
            "api_domain_name": self.__event["requestContext"]["domainName"],
            "api_path": self.__event["requestContext"]["http"]["path"],
            "api_method": self.__event["requestContext"]["http"]["method"],
            "status": "failed",
            "log_stream": os.environ["AWS_LAMBDA_LOG_STREAM_NAME"]
        }

        # check if we're sending from postman or form another site
        if "postman-token" in self.__event["headers"]:
            self.payload["origin"] = "postman"

        if "origin" in self.__event["headers"]:
            self.payload["origin"] = self.__event["headers"]["origin"]

        self.__logger.info("Notifications.set_payload: end")
