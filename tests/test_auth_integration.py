import os
import tempfile
import unittest
from unittest import mock

from auth_integration import AccessPolicy, build_access_policy, resolve_site_base_url


class AuthIntegrationTests(unittest.TestCase):
    def test_resolve_site_base_url_prefers_environment(self):
        with mock.patch.dict(os.environ, {"PRICE_SITE_BASE_URL": "https://example.test/price"}, clear=False):
            self.assertEqual(resolve_site_base_url(), "https://example.test/price")

    def test_resolve_site_base_url_defaults_to_github_pages(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(resolve_site_base_url(), "https://federicochurches.github.io/Price")

    def test_build_access_policy_uses_audit_endpoint(self):
        with mock.patch.dict(os.environ, {"PRICE_AUTH_MODE": "ad", "PRICE_AUTH_AUDIT_ENDPOINT": "https://audit.example/log"}, clear=False):
            policy = build_access_policy()
            self.assertEqual(policy.auth_mode, "ad")
            self.assertEqual(policy.audit_endpoint, "https://audit.example/log")
            self.assertIn("audit.example", policy.render_script())

    def test_access_policy_exposes_no_hardcoded_creds(self):
        policy = AccessPolicy(site_base_url="https://example.test/price")
        rendered = policy.render_script()
        self.assertNotIn("pricetravel", rendered.lower())
        self.assertNotIn("supply2026", rendered.lower())


if __name__ == "__main__":
    unittest.main()
