import argparse
import json
import re
import sys
from json import JSONDecodeError
from pathlib import Path
from typing import Any, Sequence
import requests
from labs.lab04 import analysis, api_client
from shared.student import VARIANT_NUMBER

CVE_PATTERN = re.compile(r"^CVE-[0-9]{4}-[0-9]{4,}$")

def load_response(path: Path) -> dict[str, Any]:
    """Читає локальний JSON-файл відповіді NVD"""
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError("Файл відповіді не містить JSON-об'єкт")
    return data

def _print_error(message: str) -> None:
    print(message, file=sys.stderr)

def main(argv: list[str] | None = None) -> int:
    if isinstance(VARIANT_NUMBER, bool) or not isinstance(VARIANT_NUMBER, int) or not (1 <= VARIANT_NUMBER <= 15):
        _print_error("Некоректний номер варіанта студента.")
        return 2

    parser = argparse.ArgumentParser(description="Перевірка запису CVE з NVD API")
    parser.add_argument("--cve", required=True, help="Ідентифікатор CVE")
    parser.add_argument("--input", type=Path, default=None, help="Шлях до локального JSON-файлу")

    args = parser.parse_args(argv)
    if CVE_PATTERN.fullmatch(args.cve) is None:
        _print_error("Некоректний формат ідентифікатора CVE.")
        return 2

    try:
        if args.input is not None:
            payload = load_response(args.input)
        else:
            payload = api_client.fetch_response(args.cve)
    except OSError:
        _print_error("Помилка читання файлу.")
        return 1
    except json.JSONDecodeError:
        _print_error("Помилка розбору JSON.")
        return 1
    except requests.exceptions.Timeout:
        _print_error("Перевищено час очікування запиту до NVD.")
        return 1
    except requests.exceptions.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "невідомий"
        _print_error(f"Помилка HTTP від NVD API: статус {status}.")
        return 1
    except requests.exceptions.RequestException:
        _print_error("Мережева помилка під час запиту до NVD.")
        return 1
    except ValueError:
        _print_error("Порушення структури даних відповіді.")
        return 1

    record = analysis.extract_record(payload, args.cve)
    report = analysis.build_report(record, args.cve, VARIANT_NUMBER)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())