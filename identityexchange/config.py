import json
import os
from pathlib import Path

import yaml


class Config:
    def __init__(self):
        # Ensure config directory exists
        directory = Path(os.path.join(Path.home(), ".config/identityexchange/"))
        Path(directory).mkdir(parents=True, exist_ok=True)

        self.config_path = os.path.join(directory, "application.yaml")
        self.default_config = {
            "google": {
                "credentials_file": os.path.join(Path.home(), ".config/identityexchange/google_credentials.json"),
                "domain": None
            },
            "aws": {
                "duration": 7200,
                "account": None,
                "role": None
            }
        }

    def set_google_credentials(self):
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
        path = os.path.join(Path.home(), ".config/identityexchange/google_credentials.json")
        if not os.path.isfile(path):
            with(open(path, "w")) as fb:
                fb.write(json.dumps(credentials))
                fb.flush()

    def set_config(self):
        """
        Writes the configuration file based on user input
        :return:
        """
        if os.path.isfile(self.config_path):
            return

        domain = input("Enter Google domain (only users from this domain will be allowed): ")

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
        self.default_config["aws"]["account"] = int(account_id)
        self.default_config["aws"]["role"] = role_name

        with(open(self.config_path, "w")) as fb:
            # default_flow_style ensures {} are left out of the rendered yaml
            yaml.dump(self.default_config, fb, explicit_start=True, default_flow_style=False)
            fb.flush()

    def load_config(self):
        """
        Reads configuration file and loads into a dict
        :return: (dict) configuration options
        """
        self.set_config()
        self.set_google_credentials()

        return yaml.load(open(self.config_path))
