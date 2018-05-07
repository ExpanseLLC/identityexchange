import json
import logging
import os
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)


class Config:
    def __init__(self):
        # Ensure config directory exists
        directory = Path(os.path.join(Path.home(), Config.config_dir()))
        Path(directory).mkdir(parents=True, exist_ok=True)

        self.config_path = os.path.join(directory, "application.yaml")
        self.credentials_path = os.path.join(Config.config_dir(), "credentials.json")
        self.default_config = {
            "google": {
                "credentials_file": os.path.join(Config.config_dir(), "google_credentials.json"),
                "domain": None
            },
            "aws": {
                "duration": 3600,
                "profiles": []
            }
        }

    @staticmethod
    def config_dir():
        return os.path.join(Path.home(), ".config/identityexchange/")

    @staticmethod
    def credentials_path():
        return os.path.join(Config.config_dir(), "credentials.json")

    def __set_google_credentials(self):
        """
        Writes out the google credentials file if not present on the file system
        :return:
        """
        credentials = {
            "installed": {
                "client_id": "396994310677-lka6gs28gnmgfojv5ljkp2kj3bbam4jk.apps.googleusercontent.com",
                "project_id": "megryan-poc-oauth",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://accounts.google.com/o/oauth2/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_secret": "cgSt00YeYBkcR4I_k65cmNw9",
                "redirect_uris": [
                    "urn:ietf:wg:oauth:2.0:oob",
                    "http://localhost"
                ]
            }
        }
        path = os.path.join(Config.config_dir(), "google_credentials.json")
        if not os.path.isfile(path):
            logger.debug("Writing Google credentials to {}".format(os.fspath(path)))
            with(open(path, "w")) as fb:
                fb.write(json.dumps(credentials))
                fb.flush()

    def __build_arn(self, account, role):
        """
        Constructs an AWS ARN using the account and role.
        :param account: account identifier
        :param role: IAM role name
        :return: (str) of the ARN
        """
        return "arn:aws:iam::{}:role/{}".format(account, role)

    def __set_config(self):
        """
        Writes the configuration file based on user input
        :return:
        """
        if os.path.isfile(self.config_path):
            logger.debug("Found existing application config, skipping setup")
            return

        domain = input("Enter Google domain (only users from this domain will be allowed): ")

        print("Let's configure your first AWS Profile...")
        profile_name = input("Enter the profile name: ")
        while not profile_name:
            profile_name = input("(required) Enter the profile name: ")

        account_id = input("Enter AWS account identifier: ")
        while not account_id:
            account_id = input("(required) Enter AWS account identifier: ")

        role_name = input("Enter AWS role name: ")
        while not role_name:
            role_name = input("(required) Enter AWS role name: ")

        if not domain:
            self.default_config.get("google").pop("domain")
        else:
            self.default_config["google"]["domain"] = domain

        self.default_config["aws"]["profiles"].append({
            "name": profile_name,
            "role": self.__build_arn(account_id, role_name)
        })

        logger.debug("Writing application configuration to {}".format(os.fspath(self.config_path)))
        with(open(self.config_path, "w")) as fb:
            # default_flow_style ensures {} are left out of the rendered yaml
            yaml.dump(self.default_config, fb, explicit_start=True, default_flow_style=False)
            fb.flush()

    def load_config(self):
        """
        Reads configuration file and loads into a dict
        :return: (dict) configuration options
        """
        self.__set_config()
        self.__set_google_credentials()

        return yaml.load(open(self.config_path))
