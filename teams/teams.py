import json
# 3rd party
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
                        "activityTitle": data["lambda_name"],
                        "activitySubtitle":data["function_name"],
                        "activityImage": "https://c8.alamy.com/comp/E59H30/falling-man-isolated-on-white-background-E59H30.jpg",
                        "facts": [
                            {
                                "name": "Location",
                                "value": data["location"]
                            },
                            {
                                "name": "Status",
                                "value": data["status"]
                            },
                            {
                                "name": "Description",
                                "value": data["description"]
                            }
                        ], "markdown": True
                    }],
                "potentialAction": [
                    {
                        "@type": "OpenUri",
                        "name": "View Logs",
                        "targets": [{
                            "os": "default",
                            "uri": data["logs_link"]
                        }]
                    }
                ]

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
