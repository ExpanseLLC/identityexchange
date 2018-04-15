import os
import sys
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from identityexchange import provider


class TestMethods(unittest.TestCase):

    def test_login_aws_good(self):
        expected_access_key = "12345"
        expected_secret_key = "54321"
        expected_session_token = "asdfzxcv"

        sts = MagicMock()
        sts.assume_role_with_web_identity.return_value = {
            "Credentials": {
                "AccessKeyId": expected_access_key,
                "SecretAccessKey": expected_secret_key,
                "SessionToken": expected_session_token
            }
        }

        aws = provider.AmazonWebServices(config={
            "aws": {
                "account": 1234567890,
                "duration": 3600,
                "role": "test-role"
            },
            "google": {
                "credentials": {
                    "username": "nobody",
                    "token": "123token456"
                }
            },
            "sts": sts
        })

        actual = aws.login_aws()
        sts.assume_role_with_web_identity.assert_called_once_with(
            RoleArn="arn:aws:iam::1234567890:role/test-role",
            RoleSessionName="nobody",
            WebIdentityToken="123token456",
            DurationSeconds=3600
        )
        self.assertEqual(expected_access_key, actual.get("access_key"))
        self.assertEqual(expected_secret_key, actual.get("secret_key"))
        self.assertEqual(expected_session_token, actual.get("session_token"))
