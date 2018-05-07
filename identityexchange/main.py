import argparse
import logging
import pprint

import boto3
import botocore
import oauth2client
from oauth2client import tools

from .config import Config
from .provider import Google, AmazonWebServices

pp = pprint.PrettyPrinter(indent=2)


def parse_args():
    parser = argparse.ArgumentParser(
        prog="identityexchange",
        description="Exchange public identity for AWS credentials",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[tools.argparser]
    )

    return parser.parse_args()


def setup_logging(str_log_level):
    logformat = "%(levelname)s "
    loglevel = logging._nameToLevel.get(str_log_level)

    # Debug messages show module name
    if loglevel == logging.DEBUG:
        logformat += "%(name)s - "

    logformat += "%(message)s"

    logging.basicConfig(format=logformat, level=loglevel)
    botocore.log.level = logging.WARNING
    oauth2client.client.logger.level = logging.WARNING


def main():
    """
    Application entry point
    """
    args = parse_args()
    setup_logging(args.logging_level)

    opts = Config().load_config()

    # Retrieve Google JWT token
    provider_google = Google(config=opts)
    google_credentials = provider_google.login_with_google()

    # Retrieve AWS credentials using Google token
    provider_aws = AmazonWebServices(config=opts,
                                     client=boto3.client("sts"),
                                     credentials=google_credentials)
    provider_aws.login_aws()


if __name__ == "__main__":
    main()
