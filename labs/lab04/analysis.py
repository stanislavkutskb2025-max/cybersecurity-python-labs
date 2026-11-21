import math
from typing import Any

VARIANT_RULES: dict[int, dict[str, Any]] = {
    2: {"threshold": 8.0, "field": "attackComplexity", "expected": "LOW"},
}
ALLOWED_FIELD_VALUES = {"attackComplexity": {"LOW", "HIGH"} }

def _is_non_empty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())

def _is_valid_score(value: Any) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(value)
        and 0.0 <= float(value) <= 10.0
    )
def extract_record(payload: dict[str, Any], cve_id: str) -> dict[str, Any] | None:
    """Перевіряє відповідь NVD та витягує внутрішній запис про CVE.

        Повертає None, якщо запис не знайдено, або словник із ключами:
        - vuln_status: str | None
        - description: str | None
        - cvss_version: str | None
        - score: float | None
        - score_source: str | None
        - vector: str | None
        - cvss_data: dict[str, Any] | None
        """
    if not isinstance(payload, dict):
        raise ValueError("Відповідь NVD має бути словником.")
    vulnerabilities = payload.get("vulnerabilities")
    if not isinstance(vulnerabilities, list):
        raise ValueError("Поле vulnerabilities має бути списком.")
    if len(vulnerabilities) == 0:
        return None
    if len(vulnerabilities) > 1:
        raise ValueError("Очікувався щонайбільше один запис у vulnerabilities.")

    item = vulnerabilities[0]
    if not isinstance(item, dict):
        raise ValueError("Елемент vulnerabilities має бути словником.")

    cve_obj = item.get("cve")
    if not isinstance(cve_obj, dict):
        raise ValueError("Поле cve має бути словником.")
    if cve_obj.get("id") != cve_id:
        raise ValueError("Ідентифікатор CVE у відповіді не збігається із запитаним.")

    if "vulnStatus" not in cve_obj:
        vuln_status = None
    else:
        raw_status = cve_obj["vulnStatus"]
        if not _is_non_empty_str(raw_status):
            raise ValueError("Поле vulnStatus має бути непорожнім рядком.")
        vuln_status = raw_status

    description: str | None = None
    if "descriptions" in cve_obj:
        raw_descriptions = cve_obj["descriptions"]
        if not isinstance(raw_descriptions, list):
            raise ValueError("Поле descriptions має бути списком.")
        for entry in raw_descriptions:
            if not isinstance(entry, dict):
                raise ValueError("Елемент descriptions має бути словником.")
            lang = entry.get("lang")
            val = entry.get("value")
            if not isinstance(lang, str) or not isinstance(val, str):
                raise ValueError("Поля lang та value в descriptions мають бути рядками.")
            if description is None and lang == "en" and val.strip():
                description = val
    empty_metrics_record: dict[str, Any] = {
        "vuln_status": vuln_status,
        "description": description,
        "cvss_version": None,
        "score": None,
        "score_source": None,
        "vector": None,
        "cvss_data": None,
    }

    if vuln_status is None or vuln_status == "Rejected":
        return empty_metrics_record

    if "metrics" not in cve_obj:
        return empty_metrics_record
    metrics = cve_obj["metrics"]
    if not isinstance(metrics, dict):
        raise ValueError("Поле metrics має бути словником.")

    if "cvssMetricV31" not in metrics:
        return empty_metrics_record
    metric_list = metrics["cvssMetricV31"]
    if not isinstance(metric_list, list):
        raise ValueError("Поле cvssMetricV31 має бути списком.")
    if len(metric_list) == 0:
        return empty_metrics_record

    for metric in metric_list:
        if not isinstance(metric, dict):
            raise ValueError("Елемент cvssMetricV31 має бути словником.")

    selected = next(
        (m for m in metric_list if m.get("type") == "Primary"),
        metric_list[0],
    )

    cvss_data = selected.get("cvssData")
    if not isinstance(cvss_data, dict):
        raise ValueError("Поле cvssData має бути словником.")

    raw_score = cvss_data.get("baseScore")
    if not _is_valid_score(raw_score):
        raise ValueError("Некоректне значення baseScore.")

    if "version" not in cvss_data:
        cvss_version: str | None = None
    else:
        cvss_version = cvss_data["version"]
        if not _is_non_empty_str(cvss_version) or cvss_version != "3.1":
            raise ValueError("Некоректна версія CVSS.")

    if "vectorString" not in cvss_data:
        vector: str | None = None
    else:
        vector = cvss_data["vectorString"]
        if not _is_non_empty_str(vector):
            raise ValueError("Некоректний вектор CVSS.")

    if "source" not in selected:
        score_source: str | None = None
    else:
        score_source = selected["source"]
        if not _is_non_empty_str(score_source):
            raise ValueError("Некоректне джерело оцінки.")

    return {
        "vuln_status": vuln_status,
        "description": description,
        "cvss_version": cvss_version,
        "score": float(raw_score),
        "score_source": score_source,
        "vector": vector,
        "cvss_data": dict(cvss_data),
    }


def build_report(
        record: dict[str, Any] | None,
        cve_id: str,
        variant: int,
) -> dict[str, Any]:
    """Застосовує правило варіанта та формує словник фінального звіту."""
    if isinstance(variant, bool) or not isinstance(variant, int) or variant not in VARIANT_RULES:
        raise ValueError("Некоректний номер варіанта.")

    rule = dict(VARIANT_RULES[variant])
    field = rule["field"]
    threshold = rule["threshold"]
    expected = rule["expected"]

    if record is None:
        return {
            "cve_id": cve_id,
            "variant": variant,
            "description": None,
            "vuln_status": None,
            "cvss_version": None,
            "score": None,
            "score_source": None,
            "vector": None,
            "rule": rule,
            "observed": None,
            "decision": "not_found",
        }

    vuln_status = record.get("vuln_status")
    description = record.get("description")

    if vuln_status == "Rejected":
        return {
            "cve_id": cve_id,
            "variant": variant,
            "description": description,
            "vuln_status": vuln_status,
            "cvss_version": None,
            "score": None,
            "score_source": None,
            "vector": None,
            "rule": rule,
            "observed": None,
            "decision": "rejected",
        }

    score = record.get("score")
    cvss_data = record.get("cvss_data")

    if vuln_status is None or score is None or not isinstance(cvss_data, dict):
        return {
            "cve_id": cve_id,
            "variant": variant,
            "description": description,
            "vuln_status": vuln_status,
            "cvss_version": record.get("cvss_version"),
            "score": score,
            "score_source": record.get("score_source"),
            "vector": record.get("vector"),
            "rule": rule,
            "observed": None,
            "decision": "insufficient_data",
        }

    if field not in cvss_data:
        observed: str | None = None
        decision = "insufficient_data"
    else:
        raw_observed = cvss_data[field]
        allowed_values = ALLOWED_FIELD_VALUES[field]
        if not isinstance(raw_observed, str) or raw_observed not in allowed_values:
            raise ValueError(f"Недопустиме значення поля {field}.")
        observed = raw_observed
        if score >= threshold and observed == expected:
            decision = "review"
        else:
            decision = "other"

    return {
        "cve_id": cve_id,
        "variant": variant,
        "description": description,
        "vuln_status": vuln_status,
        "cvss_version": record.get("cvss_version"),
        "score": score,
        "score_source": record.get("score_source"),
        "vector": record.get("vector"),
        "rule": rule,
        "observed": observed,
        "decision": decision,
    }






