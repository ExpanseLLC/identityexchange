import pprint

import boto3

from identityexchange import config
from .provider import Google, AmazonWebServices

pp = pprint.PrettyPrinter(indent=2)


def get_buckets(credentials):
    """
    Example function using the STS credentials received earlier.
    :param credentials: (dict) AWS STS credentials
    :return:
    """
    client = boto3.client(
        "s3",
        aws_access_key_id=credentials.get("access_key"),
        aws_secret_access_key=credentials.get("secret_key"),
        aws_session_token=credentials.get("session_token"),
    )
    pp.pprint(client.list_buckets())


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

    get_buckets(credentials=aws_credentials)


if __name__ == "__main__":
    main()
