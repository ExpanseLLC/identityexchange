import os
import sys
import unittest
from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from identityexchange import provider


class TestMethods(unittest.TestCase):

    @mock.patch("google.oauth2.id_token.verify_oauth2_token")
    def test_bad_issuer_iss(self, test_patch):
        test_patch.return_value = {
            "iss": "graph.facebook.com"
        }
        google = provider.Google(config={})
        client_id = "bogus12345"

        mock_creds = MagicMock()
        mock_creds.id_token = "bogus12345"

        with self.assertRaises(ValueError) as cm:
            google.validate_token(credentials=mock_creds, client_id=client_id)

        expected = "Wrong issuer."
        self.assertEqual(expected, str(cm.exception))

    @mock.patch("google.oauth2.id_token.verify_oauth2_token")
    def test_bad_issuer_iss_url(self, test_patch):
        test_patch.return_value = {
            "iss": "https://graph.facebook.com"
        }
        google = provider.Google(config={})
        client_id = "bogus12345"

        mock_creds = MagicMock()
        mock_creds.id_token = "bogus12345"

        with self.assertRaises(ValueError) as cm:
            google.validate_token(credentials=mock_creds, client_id=client_id)

        expected = "Wrong issuer."
        self.assertEqual(expected, str(cm.exception))

    @mock.patch("google.oauth2.id_token.verify_oauth2_token")
    def test_invalid_domain(self, test_patch):
        test_patch.return_value = {
            "iss": "accounts.google.com",
            "email": "jane.doe@google.com",
            "hd": "nobody.com"
        }
        google = provider.Google(config={
            "google": {
                "credentials": "path/to/creds",
                "domain": "somewhere.com"
            }
        })
        client_id = "bogus12345"

        mock_creds = MagicMock()
        mock_creds.id_token = "bogus12345"

        with self.assertRaises(ValueError) as cm:
            google.validate_token(credentials=mock_creds, client_id=client_id)

        expected = "Wrong hosted domain."
        self.assertEqual(expected, str(cm.exception))

    @mock.patch("google.oauth2.id_token.verify_oauth2_token")
    def test_good_token(self, test_patch):
        test_patch.return_value = {
            "iss": "accounts.google.com",
            "email": "jane.doe@google.com"
        }
        google = provider.Google(config={
            "google": {
                "credentials": "path/to/creds"
            }
        })
        client_id = "bogus12345"

        mock_creds = MagicMock()
        mock_creds.id_token = "bogus12345"

        expected = "jane.doe@google.com"
        self.assertEqual(expected, google.validate_token(credentials=mock_creds, client_id=client_id))

    @mock.patch("google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file")
    def test_login_with_google(self, test_patch):
        mock_validate_token = MagicMock(return_value="jane.doe@gmail.com")

        mock_creds = MagicMock()
        mock_creds.id_token = "bogus12345"

        mock_flow = MagicMock()
        mock_flow.run_local_server.return_value = mock_creds

        test_patch.return_value = mock_flow

        google = provider.Google(config={
            "google": {
                "credentials_file": Path("tests/credentials_file.json"),
                "domain": "somewhere.com"
            }
        })
        google.validate_token = mock_validate_token

        actual = google.login_with_google()

        mock_validate_token.assert_called_once_with(
            credentials=mock_creds,
            client_id="somethingsomething.apps.googleusercontent.com"
        )
        self.assertEqual("jane.doe@gmail.com", actual.get("username"))
        self.assertEqual("bogus12345", actual.get("token"))
