import os
from typing import Any
import requests

NVD_API_URL = "[https://services.nvd.nist.gov/rest/json/cves/2.0](https://services.nvd.nist.gov/rest/json/cves/2.0)"
REQUEST_TIMEOUT = (3.05 , 10)



def build_headers() -> dict[str, str]:
    headers = {"Accept": "application/json"}
    raw_key = os.getenv("NVD_API_KEY")
    if raw_key is not None:
        cleaned_key = raw_key.strip()
        if cleaned_key:
            headers["apiKey"] = cleaned_key
    return headers

def fetch_response(cveId: str) -> dict[str, Any]:
    response = requests.get(NVD_API_URL, params={"cveId": cveId}, headers = build_headers(), timeout=REQUEST_TIMEOUT,
                            allow_redirects=False)
    response.raise_for_status()
    if response.status_code != 200:
        raise ValueError(f"Неочікуваний HTTP-статус: {response.status_code}")
    data = response.json()
    if not isinstance(data, dict):
        raise ValueError ("Відповідь API не є JSON-об'єктом")
    return data
