import os
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import json
import logging
import argparse

@dataclass
class FileInfo:
    path: str
    hash_value: str
    size: int
    mtime: float

def get_file_info(file_path: Path, base_dir: Path) -> FileInfo:
    relative_path = str(file_path.relative_to(base_dir))

    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    hash_value = hasher.hexdigest()

    stat_info = file_path.stat()

    return FileInfo(
        path=relative_path,
        hash_value=hash_value,
        size=stat_info.st_size,
        mtime=stat_info.st_mtime
    )

def scan_directory(dir_path: Path) -> dict:
    result = {}
    for file_path in dir_path.rglob("*"):
        if file_path.is_file():
            info = get_file_info(file_path, base_dir=dir_path)
            result[info.path] = asdict(info)
    return result

def generate_baseline(dir_path: Path, baseline_path: Path):
    data = scan_directory(dir_path)

    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    with open(baseline_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def check_integrity(dir_path: Path, baseline_path: Path):
    if not baseline_path.exists():
        print(f"Помилка: {baseline_path} не існує. Запустіть спочатку 'generate'.")
        return

    logging.info(f"Loading baseline file: {baseline_path}")
    logging.info(f"Scanning directory: {dir_path}")

    with open(baseline_path, "r", encoding="utf-8") as f:
        baseline_data = json.load(f)

    current_data = scan_directory(dir_path)
    baseline_keys = set(baseline_data.keys())
    current_keys = set(current_data.keys())

    created = current_keys - baseline_keys
    deleted = baseline_keys - current_keys
    common = baseline_keys & current_keys

    modified = []
    unchanged = []

    for path in common:
        if current_data[path]["hash_value"] != baseline_data[path]["hash_value"]:
            modified.append(path)
        else:
            unchanged.append(path)

    total_files = len(current_keys | baseline_keys)

    print("\n=== File Integrity Inspection Summary ===")
    print(f"Total monitored files : {total_files}")
    print(f"Unchanged files       : {len(unchanged)}")
    print(f"Modified files        : {len(modified)}")
    print(f"Created files         : {len(created)}")
    print(f"Deleted files         : {len(deleted)}\n")

    if modified or created or deleted:
        print("=== Detected Anomalies ===")
        for path in modified:
            print(f"[MODIFIED] {path}")
            print(f"  Expected SHA-256 : {baseline_data[path]['hash_value']}")
            print(f"  Actual SHA-256   : {current_data[path]['hash_value']}")
            logging.warning(f"[MODIFIED] Змінено файл: {path}")

        for path in created:
            size = current_data[path]['size']
            print(f"[CREATED]  {path} (Size: {size} B)")
            logging.warning(f"[CREATED] Новий файл: {path}")

        for path in deleted:
            print(f"[DELETED]  {path}")
            logging.warning(f"[DELETED] Видалено файл: {path}")

        log_file_name = logging.getLogger().handlers[0].baseFilename if logging.getLogger().handlers else 'log file'
        print(f"\n[WARNING] Security alerts detected! Check audit log at {log_file_name}")

def setup_logging(log_file: Path):
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )

def main():
    parser = argparse.ArgumentParser(description="File Integrity Monitor (FIM)")

    subparsers = parser.add_subparsers(dest="command", required=True, help="Режим роботи")

    gen_parser = subparsers.add_parser("generate", help="Згенерувати еталонний baseline.json")
    gen_parser.add_argument("--dir", type=Path, default=Path("labs/lab02/data/monitored"), help="Шлях до монітореної папки")
    gen_parser.add_argument("--baseline", type=Path, default=Path("labs/lab02/data/baseline.json"), help="Шлях до baseline.json")

    check_parser = subparsers.add_parser("check", help="Перевірити цілісність файлів")
    check_parser.add_argument("--dir", type=Path, default=Path("labs/lab02/data/monitored"), help="Шлях до монітореної папки")
    check_parser.add_argument("--baseline", type=Path, default=Path("labs/lab02/data/baseline.json"), help="Шлях до baseline.json")
    check_parser.add_argument("--log-file", type=Path, default=Path("fim.log"), help="Шлях до файла логів")

    args = parser.parse_args()

    if args.command == "generate":
        generate_baseline(args.dir, args.baseline)
        print(f"Базовий стан успішно збережено у {args.baseline}!")

    elif args.command == "check":
        setup_logging(args.log_file)
        check_integrity(args.dir, args.baseline)

if __name__ == "__main__":
    main()