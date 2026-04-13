from pathlib import Path
from unittest.mock import patch

import httpx
import pytest

from paper_pilot.config import Settings
from paper_pilot.services.zotero import ZoteroService


def _settings(tmp_path: Path, **overrides: object) -> Settings:
    base = {
        "openalex_email": "you@example.com",
        "semantic_scholar_api_key": None,
        "zotero_library_id": None,
        "zotero_library_type": "user",
        "zotero_api_key": None,
        "data_dir": tmp_path,
        "libgen_mirrors": ("https://libgen.is",),
        "libgen_timeout_sec": 10.0,
        "unpaywall_email": "you@example.com",
        "zotero_local": False,
        "zotero_connector_url": "http://127.0.0.1:23119/connector/saveItems",
        "zotero_bridge_url": "http://127.0.0.1:24119",
    }
    base.update(overrides)
    return Settings(**base)


class TestLocalApiCheck:
    def test_connection_refused_returns_remediation(self, tmp_path: Path) -> None:
        service = ZoteroService(_settings(tmp_path, zotero_local=True))

        with patch.object(
            httpx.Client,
            "get",
            side_effect=httpx.ConnectError("Connection refused"),
        ):
            result = service._local_api_check()

        assert result["reachable"] is False
        assert result["error"] == "connection_refused"
        assert "remediation" in result
        assert "Zotero is running" in result["remediation"]

    def test_timeout_returns_remediation(self, tmp_path: Path) -> None:
        service = ZoteroService(_settings(tmp_path, zotero_local=True))

        with patch.object(
            httpx.Client,
            "get",
            side_effect=httpx.TimeoutException("timed out"),
        ):
            result = service._local_api_check()

        assert result["reachable"] is False
        assert result["error"] == "timeout"
        assert "remediation" in result

    def test_not_local_mode_skips_check(self, tmp_path: Path) -> None:
        service = ZoteroService(_settings(tmp_path, zotero_local=False))
        result = service._local_api_check()
        assert result["reachable"] is False
        assert result["error"] == "not_local_mode"


class TestBridgeStatus:
    def test_not_configured_returns_remediation(self, tmp_path: Path) -> None:
        service = ZoteroService(
            _settings(tmp_path, zotero_local=True, zotero_bridge_url=None)
        )
        result = service._bridge_status()
        assert result["reachable"] is False
        assert result["error"] == "not_configured"
        assert "ZOTERO_BRIDGE_URL" in result["remediation"]

    def test_connection_refused_returns_remediation(self, tmp_path: Path) -> None:
        service = ZoteroService(_settings(tmp_path, zotero_local=True))

        with patch.object(
            httpx.Client,
            "get",
            side_effect=httpx.ConnectError("Connection refused"),
        ):
            result = service._bridge_status()

        assert result["reachable"] is False
        assert result["error"] == "connection_refused"
        assert "bridge plugin" in result["remediation"]


class TestStatusIntegration:
    def test_status_includes_remediation_on_failure(self, tmp_path: Path) -> None:
        service = ZoteroService(_settings(tmp_path, zotero_local=True))

        with patch.object(
            httpx.Client,
            "get",
            side_effect=httpx.ConnectError("Connection refused"),
        ):
            status = service.status()

        assert status["local_api_reachable"] is False
        assert "local_api_remediation" in status
        assert status["local_api_error"] == "connection_refused"

    def test_status_omits_remediation_when_healthy(self, tmp_path: Path) -> None:
        service = ZoteroService(_settings(tmp_path, zotero_local=False))
        status = service.status()
        assert "local_api_remediation" not in status
        assert "bridge_remediation" not in status
