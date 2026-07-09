import unittest
from pathlib import Path
from unittest import mock

from auth_server import AuthHandler, is_within_root, _SAFE_ERROR_CODES


class IsWithinRootTests(unittest.TestCase):
    def test_child_path_is_within_root(self):
        root = Path("C:/Users/fede/Price")
        target = root / "index.html"
        self.assertTrue(is_within_root(target, root))

    def test_root_itself_is_within_root(self):
        root = Path("C:/Users/fede/Price")
        self.assertTrue(is_within_root(root, root))

    def test_sibling_dir_with_prefixed_name_is_rejected(self):
        # Price_stage starts with "Price" as a string but is NOT inside Price —
        # this is exactly the case a naive startswith() check gets wrong.
        root = Path("C:/Users/fede/Price")
        target = Path("C:/Users/fede/Price_stage/.env")
        self.assertFalse(is_within_root(target, root))

    def test_traversal_outside_root_is_rejected(self):
        root = Path("C:/Users/fede/Price")
        target = (root / ".." / "Price_stage" / ".env").resolve()
        self.assertFalse(is_within_root(target, root))


class SanitizedAuthErrorTests(unittest.TestCase):
    def test_known_error_codes_are_not_sanitized(self):
        for code in _SAFE_ERROR_CODES:
            self.assertNotEqual(code, "auth_service_unavailable")

    def test_do_post_sanitizes_unknown_error_before_sending(self):
        handler = AuthHandler.__new__(AuthHandler)
        sent = {}
        handler._send_json = lambda payload: sent.update(payload)
        handler.headers = {"Content-Length": "0"}
        handler.rfile = mock.Mock()
        handler.rfile.read.return_value = b'{"username":"jdoe","password":"x"}'
        handler.path = "/auth/validate"

        detailed = {"ok": False, "error": "connection refused (server=ldap.internal.corp, port=389)"}
        with mock.patch("auth_server.AuthenticationConfig.from_environment"):
            with mock.patch("auth_server.authenticate_ad_user", return_value=detailed):
                handler.do_POST()

        self.assertEqual(sent["error"], "auth_service_unavailable")
        self.assertNotIn("ldap.internal.corp", sent["error"])

    def test_do_post_passes_through_safe_error_codes(self):
        handler = AuthHandler.__new__(AuthHandler)
        sent = {}
        handler._send_json = lambda payload: sent.update(payload)
        handler.headers = {"Content-Length": "0"}
        handler.rfile = mock.Mock()
        handler.rfile.read.return_value = b'{"username":"jdoe","password":"x"}'
        handler.path = "/auth/validate"

        safe = {"ok": False, "error": "invalid_credentials"}
        with mock.patch("auth_server.AuthenticationConfig.from_environment"):
            with mock.patch("auth_server.authenticate_ad_user", return_value=safe):
                handler.do_POST()

        self.assertEqual(sent["error"], "invalid_credentials")


if __name__ == "__main__":
    unittest.main()
