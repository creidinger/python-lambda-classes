import json

import requests


class PulseHealth:
    """This class is an interface for the Pulse Health API

    docs: https://api-docs.pulsehealth.tech/
    """

    def __init__(self, endpoint, token, account_id, logger):
        """
        Args:
            endpoint (string): The API endpoint we're sending request to
            token (string): The API token need send from Pulse Health
            account_id (string): The Account ID send form Pulse Health
        """

        self.endpoint = endpoint
        self._TOKEN = token
        self._ACCOUNT_ID = account_id
        self.__logger = logger
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"API-TOKEN {self._ACCOUNT_ID}",
            "X-Account": self._TOKEN,
        }

    def post_contact(self, payload):
        """Send a new contact to the Pulse API

        Args:
            payload (json): The Data we're POSTing to the Pulse API

            example Payload:
            {
                "salutation": "Dr",
                "firstName": "Example",
                "middleName": "",
                "lastName": "Example",
                "specialty": "Oncology",
                "contactType": "HCP",
                "isTest": false,
                "emailAddress": "example@email.com",
                "emailIsSubscribed": true,
                "emailIsDefault": true,
                "phone": "5165551212",
                "phoneIsCallSubscribed": true,
                "phoneIsCallDefault": true,
                "phoneIsSmsSubscribed": true,
                "phoneIsSmsDefault": true,
                "customFields": {
                    "connectWithMerus": true,
                    "receiveUpdatesAboutBizengri": true
                }
            }
        """

        self.__logger.info(f"PulseHealth.post_contact: start")

        try:
            r = requests.post(self.endpoint, headers=self.headers, data=payload)
        except Exception as e:
            self.__logger.error(f"PulseHealth.post_contact: {e}")
            return {
                "status": 500,
                "message": "There was a problem posting your contact to Pulse Health.",
                "response": e,
            }

        response_dict = r.json()
        self.__logger.info(
            f"PulseHealth.post_contact: {json.dumps(response_dict, indent=4)}"
        )
        return r.json()
