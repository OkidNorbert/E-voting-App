"""
utils/helpers.py
Shared utility functions used across the application:
screen control, voter-card generation, password hashing, and audit logging.
"""
import os
import random
import string
import hashlib
import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from data.storage import AppState


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def pause() -> None:
    from utils.colors import DIM, RESET
    input(f"\n  {DIM}Press Enter to continue...{RESET}")


def generate_voter_card_number() -> str:
    """Returns a random 12-character alphanumeric voter card number."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=12))


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def log_action(state: "AppState", action: str, user: str, details: str) -> None:
    """Appends a timestamped entry to the in-memory audit log."""
    state.audit_log.append({
        "timestamp": str(datetime.datetime.now()),
        "action": action,
        "user": user,
        "details": details,
    })
