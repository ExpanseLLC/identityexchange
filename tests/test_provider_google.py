import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from identityexchange import provider


class TestMethods(unittest.TestCase):

    @patch("identityexchange.provider.run_flow")
    @patch("identityexchange.provider.flow_from_clientsecrets")
    def test_bad_issuer_iss(self, mock_client, mock_tools):
        mock_creds = MagicMock()
        mock_creds.invalid = False
        mock_creds.id_token = {
            "iss": "graph.facebook.com"
        }
        mock_creds.id_token_jwt = "jwt_token"

        mock_client.return_value = MagicMock()
        mock_tools.return_value = mock_creds

        google = provider.Google(config={
            "google": {
                "credentials_file": Path("tests/credentials_file.json"),
                "domain": "somewhere.com"
            }
        })

        mock_store = MagicMock()
        mock_store.get.return_value = mock_creds
        google.store = mock_creds

        with self.assertRaises(ValueError) as cm:
            google.login_with_google()

        expected = "Wrong issuer."
        self.assertEqual(expected, str(cm.exception))

    @patch("identityexchange.provider.run_flow")
    @patch("identityexchange.provider.flow_from_clientsecrets")
    def test_bad_issuer_iss_url(self, mock_client, mock_tools):
        mock_creds = MagicMock()
        mock_creds.invalid = False
        mock_creds.id_token = {
            "iss": "https://graph.facebook.com"
        }
        mock_creds.id_token_jwt = "jwt_token"

        mock_client.return_value = MagicMock()
        mock_tools.return_value = mock_creds

        google = provider.Google(config={
            "google": {
                "credentials_file": Path("tests/credentials_file.json"),
                "domain": "somewhere.com"
            }
        })

        mock_store = MagicMock()
        mock_store.get.return_value = mock_creds
        google.store = mock_creds

        with self.assertRaises(ValueError) as cm:
            google.login_with_google()

        expected = "Wrong issuer."
        self.assertEqual(expected, str(cm.exception))

    @patch("identityexchange.provider.run_flow")
    @patch("identityexchange.provider.flow_from_clientsecrets")
    def test_bad_domain(self, mock_client, mock_tools):
        mock_creds = MagicMock()
        mock_creds.invalid = False
        mock_creds.id_token = {
            "iss": "accounts.google.com",
            "hd": "nowhere.com"
        }
        mock_creds.id_token_jwt = "jwt_token"

        mock_client.return_value = MagicMock()
        mock_tools.return_value = mock_creds

        google = provider.Google(config={
            "google": {
                "credentials_file": Path("tests/credentials_file.json"),
                "domain": "somewhere.com"
            }
        })

        mock_store = MagicMock()
        mock_store.get.return_value = mock_creds
        google.store = mock_creds

        with self.assertRaises(ValueError) as cm:
            google.login_with_google()

        expected = "Wrong hosted domain."
        self.assertEqual(expected, str(cm.exception))

    @patch("identityexchange.provider.run_flow")
    @patch("identityexchange.provider.flow_from_clientsecrets")
    def test_good_login(self, mock_client, mock_tools):
        mock_creds = MagicMock()
        mock_creds.invalid = False
        mock_creds.id_token = {
            "iss": "accounts.google.com",
            "hd": "nowhere.com",
            "email": "jane.doe@gmail.com"
        }
        mock_creds.id_token_jwt = "jwt_token"

        mock_client.return_value = MagicMock()
        mock_tools.return_value = mock_creds

        google = provider.Google(config={
            "google": {
                "credentials_file": Path("tests/credentials_file.json"),
                "domain": "nowhere.com"
            }
        })

        mock_store = MagicMock()
        mock_store.get.return_value = mock_creds
        google.store = mock_creds

        expected = "jane.doe@gmail.com"
        response = google.login_with_google()
        self.assertEqual(expected, response.get("username"))
