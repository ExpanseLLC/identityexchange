import logging
import os
from pathlib import Path

import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow

from identityexchange.config import Config

logger = logging.getLogger(__name__)


class Google:
    def __init__(self, config):
        self.config = config
        self.store = Storage(filename=Config.credentials_path())

    def __validate_token(self, credentials):
        """
        Validates the Google OAuth2 token and retrieves the user's email address.
        :param credentials: (dict) google token credentials
        :return: (str) The user's email address
        """
        logger.debug("Validating Google token")

        idinfo = credentials.id_token
        if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            raise ValueError("Wrong issuer.")

        # If auth request is from a G Suite domain:
        google_domain = self.config.get("google").get("domain")
        if google_domain:
            logger.debug("Checking if required GSuite domain matches token")
            if idinfo["hd"] != google_domain:
                raise ValueError("Wrong hosted domain.")

        # ID token is valid. Return the user"s email from the decoded token.
        return idinfo["email"]

    def login_with_google(self):
        """
        Uses the Google OAuth2 library to perform an oauth2 authentication flow.
        :return: (dict) The username (email) and token after authentication
        """
        logger.debug("Retrieving any stored Google token")
        credentials = self.store.get()

        if not credentials or credentials.invalid:
            logger.debug("Unable to find existing valid token, running flow to get a new one")
            auth_flow = flow_from_clientsecrets(filename=self.config.get("google").get("credentials_file"),
                                                scope=["https://www.googleapis.com/auth/userinfo.email"])
            credentials = run_flow(flow=auth_flow, storage=self.store)
        else:
            logger.debug("Found existing token, refreshing")
            credentials.refresh(http=httplib2.Http())

        return {
            "username": self.__validate_token(credentials=credentials),
            "token": credentials.id_token_jwt
        }


class AmazonWebServices:
    def __init__(self, config, client, credentials):
        """
        Create a new AWS provider object
        :param config: (dict) options
        :param client: (boto3) sts client
        :param credentials: (dict) public identity provider credentials
        """
        self.config = config
        self.client = client
        self.credentials = credentials
        self.path_aws_creds = os.path.join(Path.home(), ".aws/credentials")

    def __write_aws_credentials(self, profile, credentials):
        """
        Writes out the AWS STS credentials to ~/.aws/credentials
        :param profile: (str) Name of the credential profile
        :param credentials: (dict) AWS STS credentials
        :return:
        """
        logger.debug("Saving AWS credentials for profile '{}'".format(profile))
        with open(self.path_aws_creds, "a") as fb:
            fb.writelines([
                "[{}]".format(profile),
                "\n",
                "aws_access_key_id={}".format(credentials.get("access_key")),
                "\n",
                "aws_secret_access_key={}".format(credentials.get("secret_key")),
                "\n",
                "aws_session_token={}".format(credentials.get("session_token")),
                "\n"
            ])
            fb.flush()

    def login_aws(self):
        """
        Translate a Google identity token into AWS credentials
        :return:
        """
        # clear existing store credentials
        logger.debug("Clearing out existing AWS credentials")
        open(self.path_aws_creds, "w").close()

        # load refreshed credentials
        profiles = self.config.get("aws").get("profiles", [])
        for profile in profiles:
            logger.debug("Retrieving new AWS credentials for profile '{}'".format(profile.get("name")))
            try:
                response = self.client.assume_role_with_web_identity(
                    RoleArn=profile.get("role"),
                    RoleSessionName=self.credentials["username"],
                    WebIdentityToken=self.credentials["token"],
                    DurationSeconds=self.config.get("aws").get("duration")
                )
            except Exception as e:
                logger.error("Failed to update credentials for profile '{}'".format(profile.get("name")))
                logger.error(str(e))
                continue

            sts_creds = {
                "access_key": response.get("Credentials").get("AccessKeyId"),
                "secret_key": response.get("Credentials").get("SecretAccessKey"),
                "session_token": response.get("Credentials").get("SessionToken")
            }
            self.__write_aws_credentials(profile=profile.get("name"), credentials=sts_creds)
        logger.debug("All AWS credential profiles updated")
