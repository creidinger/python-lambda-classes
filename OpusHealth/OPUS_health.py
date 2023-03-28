import os
import json
# 3rd part imports
import requests
import xmltodict


class OpusHealthPartnerInterface:
    """The OPUS Health Partner Interface web service will provide external partners with the ability to communicate with Alternative Sampling platform in real time:"""

    def __init__(self, logger):
        """

        Args:
            - logger (obj): import logger object using the singleton pattern
        """
        self.__logger = logger
        self.headers = {
            "Content-Type": "text/xml;charset=utf-8",
            "Accept-Encoding": "gzip,deflate"
        }
        self.url = None
        self.payload = None
        self.user = None
        self.password = None
        self.groupid = None

    def set_meta(self, url, user, password, groupid):
        """_summary_

        Args:
            - url (str): The API endponit we're sending the request to
            - user (str): The user account used the authenicate in the API
            - password (str): The password used the authenicate in the API
            - groupid (str): The group ID we're using to create the ID
        """

        try:
            self.url = url
            self.user = user
            self.password = password
            self.groupid = groupid

        except Exception as e:
            self.__logger.error(f"OpusHealthPartnerInterface.set_meta: {e}")
            return False

        return True

    def set_payload(self):
        """Creates the payload for the api request"""

        # build the XML payload
        self.payload = f"""
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:par="http://www.tripleiesampling.com/PartnerInterfaceWS/">
        <soapenv:Header>
            <par:ESamplingSoapHeader>
                <par:UserName>{self.user}</par:UserName>
                <par:Password>{self.password}</par:Password>
            </par:ESamplingSoapHeader>
        </soapenv:Header>
        <soapenv:Body>
            <par:GetNextAvailableDocumentNumber>
                <par:groupNumber>{self.groupid}</par:groupNumber>
            </par:GetNextAvailableDocumentNumber>
        </soapenv:Body>
    </soapenv:Envelope>"""

        self.__logger.info(
            f'OpusHealthPartnerInterface.set_payload: xmldata: {self.payload}')

    def post_request(self):
        """Send a request to the OPUS API

        Returns:
            XML: returns and xml object 
        """

        self.set_payload()

        try:
            r = requests.post(
                self.url, data=self.payload, headers=self.headers)
            self.__logger.info(
                f'OpusHealthPartnerInterface.post_request: API response status code: {r.status_code}')

        except Exception as e:
            self.__logger.error(
                f'OpusHealthPartnerInterface.post_request: API failed: \n\n {e}')

        return r

    def get_document_number(self, xml_str):
        """Extract the document number from the xml data that was recevied from the request

        Args:
            xml_str (str): Data is received as a string
        """

        # convert response xml to dict
        xml_response = xmltodict.parse(xml_str)

        self.__logger.info(
            f'OpusHealthPartnerInterface.get_document_number: xml_response \n{json.dumps(xml_response, indent=4)}')

        # get the document number
        return xml_response["soap:Envelope"]["soap:Body"]["GetNextAvailableDocumentNumberResponse"][
            "GetNextAvailableDocumentNumberResult"]["DocumentNumber"]
