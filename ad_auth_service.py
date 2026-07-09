"""Active Directory authentication service for the Price hub.

This module provides a small authentication layer that can validate a username
and password against an AD-compatible LDAP endpoint. It is designed to be used
by an HTTP endpoint or a local gateway that performs the real login check.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


def _load_env_file() -> None:
    """Merge KEY=VALUE pairs from a ``.env`` next to this module into os.environ.

    Existing environment variables always win (``os.environ.setdefault``), so a
    real deployment env / CI override is never clobbered by the file. Absent or
    unreadable ``.env`` is a no-op — the service keeps reading pure env vars.
    """
    env_path = Path(__file__).with_name(".env")
    try:
        raw = env_path.read_text(encoding="utf-8")
    except OSError:
        return
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].lstrip()
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        if key:
            os.environ.setdefault(key, value)

try:
    import ldap3
except ImportError:  # pragma: no cover - dependency may be absent in local env
    class _MissingLDAP3:  # type: ignore[no-redef]
        @staticmethod
        def Connection(*args, **kwargs):
            raise ImportError("ldap3 is not installed")

        @staticmethod
        def Server(*args, **kwargs):
            raise ImportError("ldap3 is not installed")

    ldap3 = _MissingLDAP3()


@dataclass(frozen=True)
class AuthenticationConfig:
    server: str = ""
    port: int = 636
    use_ssl: bool = True
    base_dn: str = ""
    user_dn_template: str = "{username}"

    @classmethod
    def from_environment(cls) -> "AuthenticationConfig":
        _load_env_file()
        domain = os.getenv("AD_DOMAIN", "").strip()
        server = os.getenv("AD_SERVER", "").strip()
        if not server and domain:
            server = domain
        base_dn = os.getenv("AD_BASE_DN", "").strip()
        if not base_dn and domain:
            base_dn = f"DC={domain.replace('.', ',DC=')}"
        return cls(
            server=server,
            port=int(os.getenv("AD_PORT", "636")),
            use_ssl=os.getenv("AD_USE_SSL", "true").lower() in {"1", "true", "yes"},
            base_dn=base_dn,
            user_dn_template=os.getenv("AD_USER_DN_TEMPLATE", "").strip() or "{username}",
        )


def authenticate_ad_user(username: str, password: str, config: Optional[AuthenticationConfig] = None) -> Dict[str, Any]:
    cfg = config or AuthenticationConfig.from_environment()
    if config is not None:
        # from_environment() already loads .env; do it too when a config was
        # passed in so the test-login flag / creds below reflect the file.
        _load_env_file()
    if not username or not password:
        return {"ok": False, "error": "missing_credentials"}

    # Test-login shortcut: OFF by default. Only honoured when explicitly enabled
    # via PRICE_ALLOW_TEST_LOGIN, so production authenticates against real AD.
    allow_test = os.getenv("PRICE_ALLOW_TEST_LOGIN", "").strip().lower() in {"1", "true", "yes"}
    test_user = os.getenv("PRICE_TEST_USER", "").strip()
    test_password = os.getenv("PRICE_TEST_PASSWORD", "").strip()
    if allow_test and test_user and test_password and username == test_user and password == test_password:
        return {"ok": True, "username": username, "user_dn": username, "server": "local-test"}
    if ldap3 is None:
        return {"ok": False, "error": "ldap3_not_installed"}
    if not cfg.server or not cfg.base_dn:
        return {"ok": False, "error": "authentication_not_configured"}

    domain = os.getenv("AD_DOMAIN", "").strip()
    if not domain:
        domain = os.getenv("AD_DOMAIN_FALLBACK", "").strip()
    if "@" in username or "\\" in username:
        user_dn = username
    elif cfg.user_dn_template and cfg.user_dn_template != "{username}":
        try:
            user_dn = cfg.user_dn_template.format(username=username, domain=domain)
        except KeyError:
            user_dn = cfg.user_dn_template.format(username=username)
    elif domain:
        user_dn = f"{username}@{domain}"
    else:
        user_dn = username

    candidates = []
    if cfg.server:
        candidates.append(cfg.server)
    if domain:
        candidates.append(domain)
        candidates.append(f"ldap.{domain}")
    candidates = list(dict.fromkeys(candidates))

    last_error = None
    for server_name in candidates:
        try:
            server_obj = ldap3.Server(server_name, port=cfg.port, use_ssl=cfg.use_ssl)
            conn = ldap3.Connection(
                server=server_obj,
                user=user_dn,
                password=password,
                auto_bind=False,
            )
            bind_ok = conn.bind()
            if bind_ok:
                return {"ok": True, "username": username, "user_dn": user_dn, "server": server_name}
            last_error = "invalid_credentials"
        except Exception as exc:
            last_error = f"{exc} (server={server_name}, port={cfg.port})"

    if last_error is None:
        last_error = "invalid server address"
    return {"ok": False, "error": last_error}
