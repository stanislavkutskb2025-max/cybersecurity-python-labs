import json
from pathlib import Path

import pytest
import requests

from labs.lab04 import api_client, main


def test_main_with_local_input_success(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main.main(
        ["--cve", "CVE-2099-10001", "--input", "labs/lab04/data/nvd_sample.json"]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.err == ""
    data = json.loads(captured.out)
    assert data["cve_id"] == "CVE-2099-10001"
    assert data["variant"] == 2
    assert data["decision"] == "review"


def test_main_invalid_cve_format_returns_2(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main.main(["--cve", "INVALID-123"])
    captured = capsys.readouterr()

    assert exit_code == 2
    assert captured.out == ""
    assert captured.err.strip() != ""


def test_main_missing_input_file_returns_1(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    missing_file = tmp_path / "does_not_exist.json"
    exit_code = main.main(["--cve", "CVE-2099-10001", "--input", str(missing_file)])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.out == ""
    assert captured.err.strip() != ""


def test_main_network_timeout_returns_1(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fake_fetch(_cve_id: str) -> dict[str, object]:
        raise requests.exceptions.Timeout("Timed out")

    monkeypatch.setattr(api_client, "fetch_response", fake_fetch)
    exit_code = main.main(["--cve", "CVE-2099-10001"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.out == ""
    assert captured.err.strip() != ""
