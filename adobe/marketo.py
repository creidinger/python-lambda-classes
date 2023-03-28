import os
# 3rd party imports
# source https://github.com/jepcastelein/marketo-rest-python
from marketorestpython.client import MarketoClient


class Marketo():
    """
    A class which handles posting data to Marketo
    Docs: https://developers.marketo.com/rest-api/
    """

    def __init__(self, logger):
        """
        args:
            - logger (obj): import logger object using the singleton pattern
        """
        self.munchkin_id = os.environ["munchkin_id"]  # fill in Munchkin ID, typical format 000-AAA-000
        # enter Client ID from Admin > LaunchPoint > View Details
        self.client_id = os.environ["client_id"]
        # enter Client ID and Secret from Admin > LaunchPoint > View Details
        self.client_secret = os.environ["client_secret"]
        self.api_limit = None
        self.max_retry_time = None
        # how to find list id
        # https://learn.azuqua.com/connector-reference/marketo/#:~:text=Note%3A%20in%20order%20to%20find,.marketo.com%2F%23SL2323B2.
        self.list_id = os.environ["list_id"]
        self.mc = MarketoClient(self.munchkin_id, self.client_id,
                                self.client_secret, self.api_limit, self.max_retry_time)
        self.__logger = logger

    def create_lead(self, data):
        """Upload a contact as a lead into the Marketo DB
        args:
             - data (json): the data received by the lambda function
        Response (array):
            - Success: [{'id': 43471, 'status': 'created'}]
            - Duplicate: [{'status': 'skipped', 'reasons': [{'code': '1005', 'message': 'Lead already exists'}]}]
        """

        self.__logger.info('Marketo.create_lead: Start...')

        email = data["email"]
        first_name = data["first_name"]
        last_name = data["last_name"]

        # store lead as an array
        leads = [{"email": email,
                  "firstName": first_name, "lastName": last_name}]

        try:
            # Try to create the lead
            response = self.mc.execute(method='create_update_leads', leads=leads, action='createOnly', lookupField='email',
                                       asyncProcessing='false', partitionName='Default')
        except Exception as e:
            self.__logger.info('Marketo.create_lead: failed')
            self.__logger.info(f'Marketo.create_lead: {e}')
            return None

        self.__logger.info('Marketo.create_lead: Success!')
        self.__logger.info(f'Marketo.create_lead: {response}')
        return response

    def add_to_list(self, lead_id):
        """Add a lead to a marketo list
        args:
            - lead_id (int): The ID of the lead we want to add to the list
        Response (array):
            - Success: [{'id': 43471, 'status': 'added'}]
            - Failed: {'message': 'For input string: "ST1139B2LA1" failed to convert to a number', 'code': '1001'}
        """

        self.__logger.info('Marketo.add_to_list: Start...')

        try:
            # Try to add lead to a list
            response = self.mc.execute(
                method='add_leads_to_list', listId=self.list_id, id=[lead_id])
        except Exception as e:
            self.__logger.error('Marketo.add_to_list: failed')
            self.__logger.error(f'Marketo.add_to_list: {e}')
            return None

        self.__logger.info('Marketo.add_to_list: Success!')
        self.__logger.info(f'Marketo.add_to_list: {response}')
        return response
