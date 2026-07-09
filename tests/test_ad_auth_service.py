import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from ad_auth_service import AuthenticationConfig, authenticate_ad_user


class AdAuthServiceTests(unittest.TestCase):
    def test_authenticate_ad_user_returns_success_when_bind_succeeds(self):
        class FakeConnection:
            def __init__(self, *args, **kwargs):
                self.bound = False

            def bind(self):
                self.bound = True
                return True

        with mock.patch("ad_auth_service.ldap3.Connection", FakeConnection):
            cfg = AuthenticationConfig(server="ldap.example.com", base_dn="DC=example,DC=com")
            result = authenticate_ad_user("jdoe", "secret", cfg)

        self.assertTrue(result["ok"])
        self.assertEqual(result["username"], "jdoe")

    def test_authenticate_ad_user_returns_error_when_bind_fails(self):
        class FakeConnection:
            def __init__(self, *args, **kwargs):
                pass

            def bind(self):
                return False

        with mock.patch("ad_auth_service.ldap3.Connection", FakeConnection):
            cfg = AuthenticationConfig(server="ldap.example.com", base_dn="DC=example,DC=com")
            result = authenticate_ad_user("jdoe", "wrong", cfg)

        self.assertFalse(result["ok"])
        self.assertIn("error", result)

    def test_authenticate_ad_user_returns_configured_error_when_server_not_set(self):
        cfg = AuthenticationConfig(server="", base_dn="")
        result = authenticate_ad_user("jdoe", "secret", cfg)

        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "authentication_not_configured")

    def test_environment_config_is_empty_when_not_provided(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            cfg = AuthenticationConfig.from_environment()
            self.assertEqual(cfg.server, "")
            self.assertEqual(cfg.base_dn, "")

    def test_authenticate_ad_user_uses_domain_when_username_is_plain(self):
        class FakeConnection:
            last_user = None

            def __init__(self, *args, **kwargs):
                type(self).last_user = kwargs.get("user")

            def bind(self):
                return True

        with mock.patch.dict(os.environ, {"AD_DOMAIN": "example.com", "AD_SERVER": "ldap.example.com", "AD_BASE_DN": "DC=example,DC=com"}, clear=False):
            with mock.patch("ad_auth_service.ldap3.Connection", FakeConnection):
                result = authenticate_ad_user("jdoe", "secret")

        self.assertTrue(result["ok"])
        self.assertEqual(FakeConnection.last_user, "jdoe@example.com")

    def test_environment_config_loads_basic_settings(self):
        with mock.patch.dict(os.environ, {
            "AD_SERVER": "ldap.example.com",
            "AD_PORT": "636",
            "AD_USE_SSL": "true",
            "AD_BASE_DN": "DC=example,DC=com"
        }, clear=False):
            cfg = AuthenticationConfig.from_environment()
            self.assertEqual(cfg.server, "ldap.example.com")
            self.assertEqual(cfg.port, 636)
            self.assertTrue(cfg.use_ssl)
            self.assertEqual(cfg.base_dn, "DC=example,DC=com")

    def test_environment_config_loads_values_from_dotenv_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir) / "ad_auth_service.py"
            module_path.touch()
            env_path = Path(tmpdir) / ".env"
            env_path.write_text("AD_SERVER=ldap.example.com\nAD_PORT=389\nAD_USE_SSL=false\nAD_BASE_DN=DC=example,DC=com\n", encoding="utf-8")

            with mock.patch("ad_auth_service.__file__", str(module_path)):
                with mock.patch.dict(os.environ, {}, clear=True):
                    cfg = AuthenticationConfig.from_environment()

            self.assertEqual(cfg.server, "ldap.example.com")
            self.assertEqual(cfg.port, 389)
            self.assertFalse(cfg.use_ssl)
            self.assertEqual(cfg.base_dn, "DC=example,DC=com")

    def test_test_login_shortcut_is_disabled_by_default(self):
        cfg = AuthenticationConfig(server="", base_dn="")
        with mock.patch.dict(os.environ, {"PRICE_TEST_USER": "demo", "PRICE_TEST_PASSWORD": "demo"}, clear=True):
            result = authenticate_ad_user("demo", "demo", cfg)
        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "authentication_not_configured")

    def test_test_login_shortcut_works_when_flag_enabled(self):
        cfg = AuthenticationConfig(server="", base_dn="")
        with mock.patch.dict(os.environ, {
            "PRICE_ALLOW_TEST_LOGIN": "1",
            "PRICE_TEST_USER": "demo",
            "PRICE_TEST_PASSWORD": "demo",
        }, clear=True):
            result = authenticate_ad_user("demo", "demo", cfg)
        self.assertTrue(result["ok"])
        self.assertEqual(result["server"], "local-test")

    def test_authenticate_ad_user_reports_server_details_on_bind_error(self):
        class FakeConnection:
            def __init__(self, *args, **kwargs):
                pass

            def bind(self):
                raise RuntimeError("connection refused")

        with mock.patch("ad_auth_service.ldap3.Connection", FakeConnection):
            cfg = AuthenticationConfig(server="ldap.example.com", port=389, use_ssl=False, base_dn="DC=example,DC=com")
            result = authenticate_ad_user("jdoe", "secret", cfg)

        self.assertFalse(result["ok"])
        self.assertIn("ldap.example.com", result["error"])
        self.assertIn("389", result["error"])


if __name__ == "__main__":
    unittest.main()
