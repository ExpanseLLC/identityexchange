import os
import pprint
from pathlib import Path

import boto3

from identityexchange import config
from .provider import Google, AmazonWebServices

pp = pprint.PrettyPrinter(indent=2)


def write_aws_credentials(credentials):
    """
    Writes out the AWS STS credentials to ~/.aws/credentials
    :param credentials: (dict) AWS STS credentials
    :return:
    """
    path = os.path.join(Path.home(), ".aws/credentials")
    with open(path, "w") as fb:
        fb.writelines([
            "[default]",
            "\n",
            "aws_access_key_id={}".format(credentials.get("access_key")),
            "\n",
            "aws_secret_access_key={}".format(credentials.get("secret_key")),
            "\n",
            "aws_session_token={}".format(credentials.get("session_token")),
            "\n"
        ])
        fb.flush()


def main():
    """
    Application entry point
    """
    opts = config.Config().load_config()

    provider_google = Google(config=opts)
    google_credentials = provider_google.login_with_google()

    opts["google"]["credentials"] = google_credentials
    opts["sts"] = boto3.client("sts")

    provider_aws = AmazonWebServices(config=opts)
    aws_credentials = provider_aws.login_aws()

    write_aws_credentials(credentials=aws_credentials)


if __name__ == "__main__":
    main()
