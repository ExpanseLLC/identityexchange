import json

from google.auth.transport import requests
from google.oauth2 import id_token
from google_auth_oauthlib import flow


class Google:
    def __init__(self, config):
        self.config = config

    def validate_token(self, credentials, client_id):
        """
        Validates the Google OAuth2 token and retrieves the user's email address.
        :param credentials: (dict) google token credentials
        :param client_id: (str) client id from client_credentials.json
        :return: (str) The user's email address
        """
        idinfo = id_token.verify_oauth2_token(id_token=credentials.id_token,
                                              request=requests.Request(),
                                              audience=client_id)
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
        client_credentials = json.load(open(self.config.get("google").get("credentials_file")))
        auth_flow = flow.InstalledAppFlow.from_client_secrets_file(
            self.config.get("google").get("credentials_file"),
            scopes=["profile", "email"]
        )

        credentials = auth_flow.run_local_server(host="localhost",
                                                 port=8080,
                                                 authorization_prompt_message="Please visit this URL: {url}",
                                                 success_message="Authentication complete. You may close this window.",
                                                 open_browser=True)
        return {
            "username": self.validate_token(credentials=credentials,
                                            client_id=client_credentials["installed"]["client_id"]),
            "token": credentials.id_token
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
