import copy
import json

from pathlib import Path
from typing import Any

import pytest

from labs.lab04 import analysis

SAMPLE_PATH = Path("labs/lab04/data/nvd_sample.json")


def _load_sample() -> dict[str, Any]:
    with SAMPLE_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def test_extract_record_valid_sample() -> None:
    payload = _load_sample()
    record = analysis.extract_record(payload, "CVE-2099-10001")

    assert record is not None
    assert record["vuln_status"] == "Analyzed"
    assert record["description"] == "Synthetic vulnerability for offline API testing."
    assert record["cvss_version"] == "3.1"
    assert record["score"] == 9.8
    assert record["score_source"] == "nvd@nist.gov"
    assert record["cvss_data"] is not None
    assert record["cvss_data"]["attackComplexity"] == "LOW"


def test_extract_record_empty_vulnerabilities() -> None:
    record = analysis.extract_record({"vulnerabilities": []}, "CVE-2099-10001")
    assert record is None


def test_extract_record_prefers_primary_metric() -> None:
    payload = _load_sample()
    metrics_list = payload["vulnerabilities"][0]["cve"]["metrics"]["cvssMetricV31"]
    primary = copy.deepcopy(metrics_list[0])
    secondary = copy.deepcopy(metrics_list[0])
    secondary["type"] = "Secondary"
    secondary["cvssData"]["baseScore"] = 4.2
    payload["vulnerabilities"][0]["cve"]["metrics"]["cvssMetricV31"] = [
        secondary,
        primary,
    ]

    record = analysis.extract_record(payload, "CVE-2099-10001")
    assert record is not None
    assert record["score"] == 9.8


def test_extract_record_rejected_skips_metrics() -> None:
    payload = _load_sample()
    payload["vulnerabilities"][0]["cve"]["vulnStatus"] = "Rejected"
    payload["vulnerabilities"][0]["cve"]["metrics"] = "broken-metrics-ignored"

    record = analysis.extract_record(payload, "CVE-2099-10001")
    assert record is not None
    assert record["vuln_status"] == "Rejected"
    assert record["score"] is None
    assert record["cvss_data"] is None


@pytest.mark.parametrize("bad_score", [-0.1, 10.1, "9.8", True, None, float("nan")])
def test_extract_record_invalid_score(bad_score: Any) -> None:
    payload = _load_sample()
    payload["vulnerabilities"][0]["cve"]["metrics"]["cvssMetricV31"][0]["cvssData"][
        "baseScore"
    ] = bad_score

    with pytest.raises(ValueError):
        analysis.extract_record(payload, "CVE-2099-10001")


def test_extract_record_mismatched_cve_id() -> None:
    payload = _load_sample()
    with pytest.raises(ValueError):
        analysis.extract_record(payload, "CVE-2099-99999")


def test_extract_record_multiple_vulnerabilities_raises() -> None:
    payload = _load_sample()
    payload["vulnerabilities"].append(copy.deepcopy(payload["vulnerabilities"][0]))
    with pytest.raises(ValueError):
        analysis.extract_record(payload, "CVE-2099-10001")


def test_build_report_review() -> None:
    record = analysis.extract_record(_load_sample(), "CVE-2099-10001")
    report = analysis.build_report(record, "CVE-2099-10001", variant=2)

    assert report["variant"] == 2
    assert report["observed"] == "LOW"
    assert report["decision"] == "review"


def test_build_report_other_when_score_below_threshold() -> None:
    record = analysis.extract_record(_load_sample(), "CVE-2099-10001")
    assert record is not None
    record["score"] = 7.9
    report = analysis.build_report(record, "CVE-2099-10001", variant=2)

    assert report["decision"] == "other"


def test_build_report_other_when_field_differs() -> None:
    record = analysis.extract_record(_load_sample(), "CVE-2099-10001")
    assert record is not None and record["cvss_data"] is not None
    record["cvss_data"]["attackComplexity"] = "HIGH"
    report = analysis.build_report(record, "CVE-2099-10001", variant=2)

    assert report["observed"] == "HIGH"
    assert report["decision"] == "other"


def test_build_report_not_found() -> None:
    report = analysis.build_report(None, "CVE-2099-10001", variant=2)
    assert report["decision"] == "not_found"


def test_build_report_rejected() -> None:
    record = {
        "vuln_status": "Rejected",
        "description": "Rejected CVE",
        "cvss_version": None,
        "score": None,
        "score_source": None,
        "vector": None,
        "cvss_data": None,
    }
    report = analysis.build_report(record, "CVE-2099-10001", variant=2)
    assert report["decision"] == "rejected"


def test_build_report_insufficient_data() -> None:
    record = analysis.extract_record(_load_sample(), "CVE-2099-10001")
    assert record is not None and record["cvss_data"] is not None
    del record["cvss_data"]["attackComplexity"]
    report = analysis.build_report(record, "CVE-2099-10001", variant=2)

    assert report["observed"] is None
    assert report["decision"] == "insufficient_data"


def test_build_report_invalid_field_value_raises() -> None:
    record = analysis.extract_record(_load_sample(), "CVE-2099-10001")
    assert record is not None and record["cvss_data"] is not None
    record["cvss_data"]["attackComplexity"] = "MEDIUM"

    with pytest.raises(ValueError):
        analysis.build_report(record, "CVE-2099-10001", variant=2)
