import os
import sys
import unittest
from unittest import mock
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from identityexchange import provider


class TestMethods(unittest.TestCase):

    @patch("identityexchange.provider.open")
    def test_login_aws_good(self, mock_open):
        mock_open.close.return_value = None

        expected_access_key = "12345"
        expected_secret_key = "54321"
        expected_session_token = "asdfzxcv"
        expected_username = "nobody"
        expected_token = "123token456"
        expected_duration = 3600

        mock_client = MagicMock()
        mock_client.assume_role_with_web_identity.return_value = {
            "Credentials": {
                "AccessKeyId": expected_access_key,
                "SecretAccessKey": expected_secret_key,
                "SessionToken": expected_session_token
            }
        }
        aws = provider.AmazonWebServices(
            config={
                "aws": {
                    "duration": expected_duration,
                    "profiles": [
                        {
                            "name": "test-profile",
                            "role": "arn:aws:iam::123456789101:role/test-role"
                        }
                    ]
                }
            },
            client=mock_client,
            credentials={
                "username": expected_username,
                "token": expected_token
            }
        )
        with mock.patch.object(aws, "_AmazonWebServices__write_aws_credentials", return_value=None) as mock_write:
            aws.login_aws()
            mock_write.assert_called_once_with(
                profile="test-profile",
                credentials={
                    "access_key": expected_access_key,
                    "secret_key": expected_secret_key,
                    "session_token": expected_session_token
                }
            )
            mock_client.assume_role_with_web_identity.assert_called_once_with(
                RoleArn="arn:aws:iam::123456789101:role/test-role",
                RoleSessionName=expected_username,
                WebIdentityToken=expected_token,
                DurationSeconds=expected_duration
            )
