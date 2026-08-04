from __future__ import annotations

import asyncio
import ipaddress
import socket

import pytest

from hermes_cli import web_server


def test_models_probe_rejects_private_hosts(monkeypatch):
    def fake_getaddrinfo(host, port, type=0):
        return [(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("10.0.0.5", 0))]

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)

    with pytest.raises(web_server.HTTPException) as exc:
        web_server._safe_models_probe_url("https://api.internal.example/v1")

    assert exc.value.status_code == 400
    assert "private" in str(exc.value.detail)


@pytest.mark.parametrize(
    "base_url",
    [
        "http://127.0.0.1:8000/v1",
        "http://localhost:8000/v1",
        "http://169.254.169.254/latest",
        "http://[::1]:8000/v1",
    ],
)
def test_models_probe_rejects_local_and_metadata_hosts(base_url):
    with pytest.raises(web_server.HTTPException):
        web_server._safe_models_probe_url(base_url)


def test_models_probe_allows_public_https_host(monkeypatch):
    def fake_getaddrinfo(host, port, type=0):
        assert host == "api.example.com"
        return [(socket.AF_INET, socket.SOCK_STREAM, 0, "", ("93.184.216.34", 0))]

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)

    assert web_server._safe_models_probe_url("https://api.example.com/v1") == "https://api.example.com/v1/models"


def test_models_probe_rejects_mixed_public_and_private_dns(monkeypatch):
    def fake_getaddrinfo(host, port, type=0):
        return [
            (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("93.184.216.34", 0)),
            (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("127.0.0.1", 0)),
        ]

    monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)

    assert not web_server._is_public_probe_address("api.example.com")


def test_profile_terminal_opener_does_not_use_shell(monkeypatch):
    calls = []

    monkeypatch.setattr(web_server.sys, "platform", "linux")
    monkeypatch.setattr(web_server, "_profile_setup_argv", lambda name: ["safe-profile", "setup"])
    monkeypatch.setattr(web_server.subprocess, "call", lambda *args, **kwargs: 0)
    monkeypatch.setattr(web_server.subprocess, "Popen", lambda args, **kwargs: calls.append(args))

    result = asyncio.run(web_server.open_profile_terminal_endpoint("safe-profile"))

    assert result == {"ok": True, "command": "safe-profile setup"}
    assert calls == [["x-terminal-emulator", "-e", "safe-profile", "setup"]]
    flattened = [part for call in calls for part in call]
    assert "sh" not in flattened
    assert "-lc" not in flattened
