from datetime import datetime
import os
import json
import xml.etree.ElementTree as ET
# 3rd party imports
import paramiko


class MerkleSftp():
    """This is an interface for the FPT with Merkle"""

    def __init__(self, logger, stage, data):
        """
        Args:
            logger (obj): import logger object using the singleton pattern
            stage (str): A string indicating wither we are in staging or Prod
                Ex: 
                    - prod
                    - test
            data (dict): The data we received from the POST
        """
        self.stage = stage
        self.__logger = logger
        # get the meta data needed for the payload
        self.meta = json.loads(os.environ["mrkle_meta"])
        self.data = data
        self.ftp_username = None
        self.ftp_password = None
        self.filename = self.set_filename()
        self.payload_str = self.build_payload()
        self.set_credentials()

    def set_credentials(self):
        """Set the username and password for the FTP"""

        self.__logger.info("MerkleSftp.set_credentials: start")
        self.__logger.info(f"MerkleSftp.set_credentials: useing {self.stage}")

        if self.stage == "prod":
            self.ftp_username = os.environ["ftp_username_prod"]
            self.ftp_password = os.environ["ftp_password_prod"]
            return

        self.ftp_username = os.environ["ftp_username_test"]
        self.ftp_password = os.environ["ftp_password_test"]

    def build_xml_prop(self):
        """Builds the xml proerty for the open ended question has prescription

        Note: The mapping for this data can be found in the Code Spec file provided by Merkle
        """

        if int(self.data['contact_type']) == 2:
            # yes
            if self.data["has_prescription"]:
                return f'<Answer AnswerID="1" OpenEndedQuestionInd="N" QuestionID="9842"/>'
            # No
            return f'<Answer AnswerID="2" OpenEndedQuestionInd="N" QuestionID="9842"/>'

        if int(self.data['contact_type']) == 3:
            # yes
            if self.data["has_prescription"]:
                return f'<Answer AnswerID="1" OpenEndedQuestionInd="N" QuestionID="9843"/>'
            # No
            return f'<Answer AnswerID="2" OpenEndedQuestionInd="N" QuestionID="9843"/>'

        # default return
        return ""

    def build_payload(self):
        """Build the payload that will be sent to the FTP"""

        self.__logger.info("MerkleSftp.build_payload: building...")

        # get the current timestamp and format it
        now = datetime.now()
        date_time_str = now.strftime("%Y-%m-%dT%H:%M:%S")

        has_prescription = self.build_xml_prop()

        payload = f"""<?xml version="1.0" encoding="UTF-8"?>
<Interactions>
<Interaction ExternalID="{self.meta['ExternalID']}" SourceCode="{self.meta['SourceCode']}" VendorCode="{self.meta['VendorCode']}" ChannelCode="{self.meta['ChannelCode']}" ProductCode="{self.meta['ProductCode']}">
<Consumer AddressLine1="{self.data['address']}" CaptureDate="{date_time_str}" City="{self.data['city']}" EmailAddress="{self.data['email']}" FirstName="{self.data['firstname']}" LastName="{self.data['lastname']}" State="{self.data['state']}" ZipCodeBase="{self.data['zipcode']}"/>
<Campaign CampaignCode="{self.meta['CampaignCode']}" PromoCode="{self.meta['PromoCode']}" KitCode="{self.meta['KitCode']}" OfferCode="{self.meta['OfferCode']}"/>
<Response ResponseDate="{date_time_str}" MediaOriginCode="{self.meta['MediaOriginCode']}"/>
	<Survey SurveyDate="{date_time_str}">
			<Answers>
				<Answer AnswerID="1" OpenEndedQuestionInd="N" QuestionID="9840"/>
				<Answer AnswerID="{self.data['contact_type']}" OpenEndedQuestionInd="N" QuestionID="9841"/>
				{has_prescription}
			</Answers>
		</Survey>
	</Interaction>
</Interactions>
"""
        self.__logger.info(f"MerkleSftp.build_payload: end:\n{payload}")

        return payload

    def convert_to_xml(self):
        """Convert the xml sting to actualy XML"""

        self.__logger.info("MerkleSftp.convert_to_xml: converting...")

        return ET.fromstring(self.payload_str)

    def set_filename(self):
        """create the filename of the xml file"""
        # File naming instructions from Merkle
        #
        # <CLIENT_NAME>_<BRAND_CD*>_CNSMR_<CHANNEL**>_<ccyymmddhhmiss>_<rec_count>.xml
        # ** The following values can be used for Channel:
        # W – Web
        # E – Email
        # H – Hard Copy includes direct mail, BRC, vouchers, etc.
        # T – IVR/Teleservice
        # M – Mixed within multiple channels within XML Underscore ( _ )
        #
        # An example would be <CLIENT_NAME>_RK1_CNSMR_W_20230207132914_4.xml

        # get the current time and append to file
        now = datetime.now()
        date_time_str = now.strftime("%Y%m%d%H%M%S")

        self.__logger.info("MerkleSftp.set_filename: start")

        filename = f"_{self.meta['ProductCode']}_CNSMR_W_{date_time_str}_4.xml"

        self.__logger.info(
            f"MerkleSftp.set_filename: end - filename {filename}")

        return filename

    def save_temp_payload_file(self):
        """Save xml data to the tmp directory"""

        self.__logger.info("MerkleSftp.save_temp_payload_file: start")

        # convert string to xml
        xml_data = self.convert_to_xml()

        # save the file to the /tmp directory
        xml_tree = ET.ElementTree(xml_data)
        xml_tree.write(f"/tmp/{self.filename}")

        self.__logger.info("MerkleSftp.save_temp_payload_file: end")

    def transfer_data(self):
        """Send data to the Merkle FTP

        docs: https://docs.paramiko.org/en/stable/index.html
        """

        self.__logger.info("MerkleSftp.transfer_data: start")

        # save the data as a file and the tmp directory
        self.save_temp_payload_file()

        # file Transfer Example...
        # source: https://stackoverflow.com/questions/3635131/paramikos-sshclient-with-sftp

        # Create an sftp transport
        self.__logger.info("MerkleSftp.transfer_data: Create a transport")
        transport = paramiko.Transport((os.environ["ftp_host"], 22))

        # connect to server
        self.__logger.info("MerkleSftp.transfer_data: connect to server")
        transport.connect(None, self.ftp_username, self.ftp_password)

        self.__logger.info(
            "MerkleSftp.transfer_data: Try creating an sftp client")
        try:
            sftp = paramiko.SFTPClient.from_transport(transport)
            self.__logger.info(sftp)

            # create paths
            localpath = f"/tmp/{self.filename}"
            filepath = f"/Inbox/{self.filename}"

            sftp.put(localpath, filepath)

            sftp.close()
            transport.close()

        except Exception as e:
            self.__logger.error("MerkleSftp.transfer_data: Failed")
            self.__logger.error(f"MerkleSftp.transfer_data: {e}")

        self.__logger.info("MerkleSftp.transfer_data: end")
