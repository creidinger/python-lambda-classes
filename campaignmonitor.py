import os
import json
# 3rd party
import requests


class CampaignMonitor:
    """A Class which handles integration with the campaign monitor api."""

    def __init__(self, logger):
        """args:
            - logger (obj): import logger object using the singleton pattern
        """
        self.__logger = logger
        self.__CLIENT_ID = os.environ["client_id"]
        self.__API_KEY = os.environ["api_key"]
        self.__LIST_API_ID = os.environ["list_api_id"]
        self.__PASSWORD = os.environ["password"]
        self.__SUBSCRIBER_API_URL = f"https://api.createsend.com/api/v3.3/subscribers/{self.__LIST_API_ID}.json"
        self.__HEADERS = {
            'Content-Type': 'application/json',
        }

    def add_subscriber_to_list(self, payload):
        """Posts data received from amzeeq.com to the campaing monitor api

        source: https://www.campaignmonitor.com/api/v3-3/subscribers/

        Args:
            payload (dict): the data received by from amzeeq.com

        payload example:
        {
            "EmailAddress": "post@man.com",
            "Name": "Post Man",
            "CustomFields": [
                {
                    "Key": "Zip",
                    "Value": 99999,
                }
            ],
            "Resubscribe": true,
            "RestartSubscriptionBasedAutoresponders": true,
            "ConsentToTrack": "Unchanged"
        }

        Success response: "post@man.com"
        """

        self.__logger.info("CampaignMonitor.add_subscriber_to_list: start")
        self.__logger.info(
            f"CampaignMonitor.add_subscriber_to_list: payload: {payload}")

        try:
            r = requests.post(self.__SUBSCRIBER_API_URL, auth=(self.__API_KEY, self.__PASSWORD),
                              headers=self.__HEADERS, data=payload)
        except Exception as e:
            self.__logger.error(f"CampaignMonitor.add_subscriber_to_list: {e}")
            return False

        self.__logger.info(
            f"CampaignMonitor.add_subscriber_to_list: {r.text}")
        self.__logger.info(
            f"CampaignMonitor.add_subscriber_to_list: status_code: {r.status_code}")

        # Fail
        if r.status_code != 201:
            return False

        # success
        return True
