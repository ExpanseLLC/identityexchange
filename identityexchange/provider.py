import httplib2
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow

from identityexchange.config import Config


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
        idinfo = credentials.id_token
        if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            raise ValueError("Wrong issuer.")

        # If auth request is from a G Suite domain:
        google_domain = self.config.get("google").get("domain")
        if google_domain:
            if idinfo["hd"] != google_domain:
                raise ValueError("Wrong hosted domain.")

        # ID token is valid. Return the user"s email from the decoded token.
        return idinfo["email"]

    def login_with_google(self):
        """
        Uses the Google OAuth2 library to perform an oauth2 authentication flow.
        :return: (dict) The username (email) and token after authentication
        """
        credentials = self.store.get()

        if not credentials or credentials.invalid:
            # could not find existing credentials, run the flow
            auth_flow = flow_from_clientsecrets(filename=self.config.get("google").get("credentials_file"),
                                                scope=["https://www.googleapis.com/auth/userinfo.email"])
            credentials = run_flow(flow=auth_flow, storage=self.store)
        else:
            # refresh the token we found
            credentials.refresh(httplib2.Http())

        return {
            "username": self.__validate_token(credentials=credentials),
            "token": credentials.id_token_jwt
        }


class AmazonWebServices:
    def __init__(self, config):
        """
        Create a new AWS provider object
        :param config: (dict) options
        """
        self.config = config

    def login_aws(self):
        """
        Translate a Google identity token into AWS credentials
        :return: (dict) AWS credential set
        """
        response = self.config.get("sts").assume_role_with_web_identity(
            RoleArn="arn:aws:iam::{}:role/{}".format(
                self.config.get("aws").get("account"),
                self.config.get("aws").get("role"),
            ),
            RoleSessionName=self.config.get("google").get("credentials")["username"],
            WebIdentityToken=self.config.get("google").get("credentials")["token"],
            DurationSeconds=self.config.get("aws").get("duration")
        )
        return {
            "access_key": response.get("Credentials").get("AccessKeyId"),
            "secret_key": response.get("Credentials").get("SecretAccessKey"),
            "session_token": response.get("Credentials").get("SessionToken")
        }
