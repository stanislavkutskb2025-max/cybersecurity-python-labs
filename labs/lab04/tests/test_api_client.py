import pytest
import requests

from labs.lab04 import api_client


class DummyResponse:
    """Імітація HTTP-відповіді бібліотеки requests."""

    def __init__(
        self, status_code: int, payload: object, raise_http_error: bool = False
    ):
        self.status_code = status_code
        self.payload = payload
        self.raise_http_error = raise_http_error

    def raise_for_status(self) -> None:
        if self.raise_http_error:
            raise requests.exceptions.HTTPError("HTTP error")

    def json(self) -> object:
        return self.payload


def test_build_headers_without_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("NVD_API_KEY", raising=False)
    assert api_client.build_headers() == {"Accept": "application/json"}


def test_build_headers_with_valid_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NVD_API_KEY", "  my-secret-key  ")
    assert api_client.build_headers() == {
        "Accept": "application/json",
        "apiKey": "my-secret-key",
    }


def test_fetch_response_success(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    def fake_get(url: str, **kwargs: object) -> DummyResponse:
        captured["url"] = url
        captured.update(kwargs)
        return DummyResponse(200, {"vulnerabilities": []})

    monkeypatch.setattr(requests, "get", fake_get)
    result = api_client.fetch_response("CVE-2021-44228")

    assert result == {"vulnerabilities": []}
    assert captured["url"] == api_client.NVD_API_URL
    assert captured["params"] == {"cveId": "CVE-2021-44228"}
    assert captured["timeout"] == api_client.REQUEST_TIMEOUT
    assert captured["allow_redirects"] is False


def test_fetch_response_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        requests, "get", lambda *a, **kw: DummyResponse(404, {}, raise_http_error=True)
    )
    with pytest.raises(requests.exceptions.HTTPError):
        api_client.fetch_response("CVE-2021-44228")


def test_fetch_response_unexpected_status(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        requests, "get", lambda *a, **kw: DummyResponse(201, {"ok": True})
    )
    with pytest.raises(ValueError):
        api_client.fetch_response("CVE-2021-44228")


def test_fetch_response_non_dict_json(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        requests, "get", lambda *a, **kw: DummyResponse(200, ["not", "a", "dict"])
    )
    with pytest.raises(ValueError):
        api_client.fetch_response("CVE-2021-44228")


def test_build_headers_with_whitespace_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NVD_API_KEY", "   ")
    assert api_client.build_headers() == {"Accept": "application/json"}
