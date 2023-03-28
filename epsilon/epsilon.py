import json
# 3rd party
import requests


class Epsilon:
    """An interface for handling request to the Eplison API"""

    def __init__(self, logger, api_region, api_key):
        """_summary_

        Args:
            logger (obj): import logger object using the singleton pattern
            apikey (str): The api key for the Epsilon API
        """

        self.__logger = logger
        self.api_region = api_region
        # private variables
        self.__api_key = api_key
        self.__registration_token = None
        self.__data_param = None  # (obj) The data being sent as a paramenter
        # (obj) the profile being sent as a parameter
        self.__profile_param = None

    def set_registration_token(self):
        """
        Start the Epsilon registration process by requesting a
        `registration_token` from the `accoutns.initRegiration` endpoint.
        """

        self.__logger.info('Epsilon.set_registration_token: start')

        endpoint = f'{self.api_region}/accounts.initRegistration'

        params = {
            'isLite': True,
            'apiKey': self.__api_key
        }

        try:
            r = requests.post(endpoint, params=params)

        except Exception as e:
            # critical lambda failture
            self.__logger.error('Epsilon.set_registration_token: failed!!!')
            self.__logger.error(
                f'Epsilon.set_registration_token: endpoint: {endpoint}')
            self.__logger.error(
                f'Epsilon.set_registration_token: params: {params}')
            self.__logger.error(f'Epsilon.set_registration_token: {e}')

            return False

        # if the request is 400 or greater,
        # return an error
        if not r.ok:
            self.__logger.error('Epsilon.set_registration_token: failed!!!')
            self.__logger.error(
                f'Epsilon.set_registration_token: endpoint: {endpoint}')
            self.__logger.error(
                f'Epsilon.set_registration_token: params: {params}')
            self.__logger.error(f'Epsilon.set_registration_token: {r.text}')

            return False

        self.__logger.info(
            f'Epsilon.set_registration_token: response: \n{json.dumps(r.json(), indent=4)}')

        # get the token from the response
        resp_dict = r.json()

        # set the token
        self.__registration_token = resp_dict["regToken"]

        self.__logger.info(
            f'Epsilon.set_registration_token: token Set: {self.__registration_token}')

        self.__logger.info('Epsilon.set_registration_token: Success')

        return True

    def post_registration(self, data):
        """Try to send a POST to the `setAccountInfo`endpoint

        Args:
            data (obj): The payload received from the lambda event
        """

        self.__logger.info('Epsilon.post_registration: start')

        # buid parameters
        self.build_profile_param(data=data)
        self.build_data_param(data=data)

        endpoint = f'{self.api_region}/accounts.setAccountInfo'

        params = {
            'regToken': self.__registration_token,
            'profile': self.__profile_param,
            'data': self.__data_param
        }

        try:
            r = requests.post(endpoint, params=params)

        except Exception as e:
            # critical lambda failture
            self.__logger.error('Epsilon.post_registration: failed!!!')
            self.__logger.error(
                f'Epsilon.post_registration: endpoint: {endpoint}')
            self.__logger.error(
                f'Epsilon.post_registration: params: {params}')
            self.__logger.error(f'Epsilon.post_registration: {e}')

            return False

        # if the request is 400 or greater,
        # return an error
        if not r.ok:
            self.__logger.error('Epsilon.post_registration: failed!!!')
            self.__logger.error(
                f'Epsilon.post_registration: endpoint: {endpoint}')
            self.__logger.error(
                f'Epsilon.post_registration: params: {params}')
            self.__logger.error(f'Epsilon.post_registration: {r.text}')

            return False

        self.__logger.info(
            f'Epsilon.post_registration: response: \n{json.dumps(r.json(), indent=4)}')

        self.__logger.info('Epsilon.post_registration: end')

        return True

    def build_profile_param(self, data):
        """Take the data from the event and create the `profile` parameter.

        Args:
            data (obj): The payload received from the lambda event
        """

        self.__logger.info('Epsilon.build_profile_param: start')

        # fill out template
        profile = {
            "firstName": data["firstname"],
            "lastName": data["lastname"],
            "email": data["email"],
            "zip": data["zip"],
            "address": data["address"],
            "city": data["city"],
            "state": data["state"]
        }

        # set the profile
        self.__profile_param = json.dumps(profile)

        self.__logger.info(
            f'Epsilon.build_profile_param: profile:\n{self.__profile_param}')

        self.__logger.info('Epsilon.build_profile_param: end')

    def build_data_param(self, data):
        """Take the data from the event and create the `data` parameter.

        Args:
            data (obj): The payload received from the lambda event
        """

        self.__logger.info('Epsilon.build_data_param: start')

        # fill out template
        event_data = {
            "profile_registration_source": "Intouch",
            "profile_identity_type_hcp_hco": "Y",
            "profile_title": data["title"],
            "profile_hcp_hco_credential_type": data["credential_type"],
            "brand_adlarity_hcp_hco_enrollment_channel": "WEB",
            "brand_adlarity_hcp_hco_channel_pref_email": True,
            "brand_adlarity_hcp_hco_channel_pref_email_date": data["date"],
            "global_opt_out_all_marketing_comms": False,
            "global_opt_out_all_marketing_comms_date": data["date"],
            "profile_specialty": data["specialty"],
            "terms": True,
            "brand_adlarity_hcp_hco_channel_pref_rep_email": data["email"],
            "brand_adlarity_hcp_hco_channel_pref_rep_email_date": data["date"],
            "brand_adlarity_hcp_hco_rep_request": data["rep_request"],
            "brand_adlarity_hcp_hco_rep_request_date": data["date"],
            "brand_adlarity_hcp_hco_med_liaison_request": data["liason_request"],
            "brand_adlarity_hcp_hco_med_liaison_request_date": data["date"],
            "brand_adlarity_hcp_hco_rep_request_sample": data["request_sample"]
        }

        # set the profile
        self.__data_param = json.dumps(event_data)

        self.__logger.info(
            f'Epsilon.build_data_param: data:\n{self.__data_param}')

        self.__logger.info('Epsilon.build_data_param: end')
