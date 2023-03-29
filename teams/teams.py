import json
import requests


class MsTeams:
    """A general purpose interface for Microsoft Teams

    docs: https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/connectors-using?tabs=cURL
    """

    def __init__(self, logger) -> None:
        """

        Args:
            logger (obj): import logger object using the singleton pattern
        """
        self.__logger = logger
        self.__payload = None

    def build_payload(self, data):
        """Build a payload that will be send via Teams

        Args:
            data (dict): The event data recived when lambda was invoked.
        """

        self.__logger.info("MsTeams.build_payload: start")

        try:
            self.__payload = {
                "@type": "MessageCard",
                "summary": "Lambda Failure!!!",
                "sections": [
                    {
                        "activityTitle": f'Lambda Name: {data["lambda_name"]}',
                        "activitySubtitle": f'Failing Function Name: {data["function_name"]}',
                        "activityImage": "https://cdn3.vectorstock.com/i/1000x1000/02/52/pirate-skull-icon-vector-11230252.jpg",
                        "facts": [
                            {
                                "name": "Description",
                                "value": data["description"]
                            },
                            {
                                "name": "Origin",
                                "value": data["origin"]
                            },
                            {
                                "name": "Api Domain Name",
                                "value": data["api_domain_name"]
                            },
                            {
                                "name": "Api Path",
                                "value": data["api_path"]
                            },
                            {
                                "name": "Api Method",
                                "value": data["api_method"]
                            },
                            {
                                "name": "Status",
                                "value": data["status"]
                            },
                            {
                                "name": "Log Stream",
                                "value": data["log_stream"]
                            }
                        ], "markdown": True
                    }]
            }

        except Exception as e:
            self.__logger.error("MsTeams.build_payload: Failed!!!")
            self.__logger.error(f"MsTeams.build_payload: {e}")
            return False

        self.__logger.info("MsTeams.build_payload: end")
        return True

    def send_webhook_message_to_channel(self, webhook_url):
        """_summary_

        Args:
            webhook_url (str): The webhook url of the teams channel we're tring to send data to.
        """

        self.__logger.info("MsTeams.send_webhook_message_to_channel: start")

        headers = {
            "Content-type": "application/json",
        }

        try:
            r = requests.post(webhook_url, headers=headers,
                              json=self.__payload)
        except Exception as e:
            self.__logger.error(
                "MsTeams.send_webhook_message_to_channel: Failed!!!")
            self.__logger.error(
                f"MsTeams.send_webhook_message_to_channel: {e}")
            return False

        # The Webhook post failed
        if not r.ok:
            self.__logger.error(
                "MsTeams.send_webhook_message_to_channel: Failed!!!")
            self.__logger.error(
                f"MsTeams.send_webhook_message_to_channel: status_code: {r.status_code}")
            self.__logger.error(
                f"MsTeams.send_webhook_message_to_channel: response: {r.text}")
            return False

        self.__logger.info("MsTeams.send_webhook_message_to_channel: end")
        return True
