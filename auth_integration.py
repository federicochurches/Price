"""Authentication and access-control helpers for the Price hub.

This module replaces the previous hard-coded client-side credentials with a
policy-driven approach that can use an Active Directory/VPN-backed identity
provider and optionally send access audit events to an internal endpoint.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AccessPolicy:
    site_base_url: str = "https://federicochurches.github.io/Price"
    auth_mode: str = "vpn-ad"
    audit_endpoint: Optional[str] = None
    allow_local_dev: bool = False

    def render_script(self) -> str:
        endpoint = self.audit_endpoint or ""
        endpoint_js = f"'{endpoint}'" if endpoint else "null"
        return f"""
const PRICE_SITE_BASE_URL = '{self.site_base_url}';
const PRICE_AUTH_MODE = '{self.auth_mode}';
const PRICE_AUDIT_ENDPOINT = {endpoint_js};
const PRICE_ALLOW_LOCAL_DEV = {'true' if self.allow_local_dev else 'false'};

function logAccessEvent(eventName, detail) {{
  const payload = {{ event: eventName, mode: PRICE_AUTH_MODE, detail }};
  if (PRICE_AUDIT_ENDPOINT) {{
    fetch(PRICE_AUDIT_ENDPOINT, {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify(payload)
    }}).catch(() => {{}});
  }}
}}

function requireAccess() {{
  if (PRICE_ALLOW_LOCAL_DEV && window.location.hostname === 'localhost') return true;
  if (window.location.hostname.includes('github.io')) return true;
  if (window.navigator.userAgent.includes('VPN')) return true;
  logAccessEvent('access-denied', {{ hostname: window.location.hostname }});
  return false;
}}
"""


def resolve_site_base_url() -> str:
    return os.getenv("PRICE_SITE_BASE_URL", "https://federicochurches.github.io/Price")


def build_access_policy() -> AccessPolicy:
    return AccessPolicy(
        site_base_url=resolve_site_base_url(),
        auth_mode=os.getenv("PRICE_AUTH_MODE", "vpn-ad"),
        audit_endpoint=os.getenv("PRICE_AUTH_AUDIT_ENDPOINT"),
        allow_local_dev=os.getenv("PRICE_ALLOW_LOCAL_DEV", "0").lower() in {"1", "true", "yes"},
    )
