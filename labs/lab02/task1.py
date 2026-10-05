import hashlib
import os
import hmac
import re
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Any

EMAIL_REGEX = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]{2,63}@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
PBKDF2_ITERATIONS = 100_000


class User:
    def __init__(self, username: str, email: str, role: str, active: bool = True):

        self.username = username
        self.email = email
        self.role = role
        self.active = active

        self.__password_hash: str | None = None
        self.__password_salt: str | None = None

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        if not isinstance(value, str) or not EMAIL_REGEX.match(value):
            raise ValueError(f"Некоректний формат email: '{value}'")
        self._email = value

    def set_password(self, password: str) -> None:

        salt = os.urandom(16)

        key = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
        )

        self.__password_salt = salt.hex()
        self.__password_hash = key.hex()

    def check_password(self, password: str) -> bool:
        if not self.__password_hash or not self.__password_salt:
            return False

        salt = bytes.fromhex(self.__password_salt)
        new_key = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
        )
        return hmac.compare_digest(new_key.hex(), self.__password_hash)

    def deactivate(self) -> None:
        self.active = False

    def __str__(self):
        status = "active" if self.active else "inactive"
        return f"User(username='{self.username}', email='{self.email}', role='{self.role}', status={status})"


class Admin(User):
    def __init__(
        self,
        username: str,
        email: str,
        permissions: set[str] | list[str] | None = None,
        role: str = "admin",
        active: bool = True,
    ):
        super().__init__(username=username, email=email, role=role, active=active)

        if permissions is None:
            self.permissions: set[str] = set()
        else:
            self.permissions = set(permissions)

    def grant_permission(self, permission: str) -> None:
        self.permissions.add(permission)

    def revoke_permission(self, permission: str) -> None:
        self.permissions.discard(permission)

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    def __str__(self) -> str:
        base_str = super().__str__()
        return f"{base_str} | Permissions count: {len(self.permissions)}"


class Session:
    def __init__(
        self, ip: str, login_time: datetime = None, last_activity: datetime = None
    ) -> None:

        self.ip = ip
        now_utc = datetime.now(timezone.utc)
        self.login_time = login_time if login_time is not None else now_utc
        self.last_activity = last_activity if last_activity is not None else now_utc

    def touch(self) -> None:
        self.last_activity = datetime.now(timezone.utc)

    def is_active(self, timeout_sec: int = 300) -> bool:
        if timeout_sec <= 0:
            raise ValueError("timeout_sec повинен бути додатним числом (> 0)")

        now = datetime.now(timezone.utc)
        elapsed_time = now - self.last_activity

        return elapsed_time.total_seconds() < timeout_sec


@dataclass
class AuditRecord:
    timestamp: datetime
    username: str
    action: str


class AuditLog:
    def __init__(self, logs: list[AuditRecord] | None = None) -> None:
        self.logs: list[AuditRecord] = logs if logs is not None else []

    def add_log(self, username: str, action: str) -> None:
        now = datetime.now(timezone.utc)
        record = AuditRecord(timestamp=now, username=username, action=action)
        self.logs.append(record)

    def show_all(self) -> None:
        if not self.logs:
            print("Журнал аудиту порожній.")
            return
        for record in self.logs:
            formatted_time = record.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
            print(
                f"[{formatted_time}] User: {record.username} | Action: {record.action}"
            )


SESSION_TIMEOUT_SEC = 900
ALLOWED_KEYS = {"user": User, "session": (Session, type(None)), "audit_log": AuditLog}


class UserAccount:
    def __init__(
        self,
        user: User,
        session: Session | None = None,
        audit_log: AuditLog | None = None,
    ) -> None:
        self.user = user
        self.session = session
        self.audit_log = audit_log

    def login(self, username: str, password: str, ip: str) -> bool:
        if username == self.user.username and self.user.check_password(password):
            self.session = Session(ip)
            self.session.touch()
            self.audit_log.add_log(username, "login_success")
            return True
        else:
            self.audit_log.add_log(username, "login_failure")
            return False

    def is_authenticated(self) -> bool:
        if self.session is not None:
            return self.session.is_active(SESSION_TIMEOUT_SEC)
        else:
            return False

    def logout(self) -> None:
        self.audit_log.add_log(self.user.username, "logout_success")
        self.session = None

    def __getitem__(self, key: str):
        if key not in ALLOWED_KEYS:
            raise KeyError(f"Ключ '{key}' не дозволений або не існує")
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        if key not in ALLOWED_KEYS:
            raise KeyError(f"Ключ '{key}' не дозволений або не існує")
        expected_type = ALLOWED_KEYS[key]
        if not isinstance(value, expected_type):
            raise TypeError(f"Значення для '{key}' має бути типу {expected_type}")

        setattr(self, key, value)
