"""
models/admin.py
Admin domain model.
"""
from dataclasses import dataclass


@dataclass
class Admin:
    id: int
    username: str
    password: str
    full_name: str
    email: str
    role: str          # super_admin | election_officer | station_manager | auditor
    created_at: str
    is_active: bool

    def to_dict(self) -> dict:
        return self.__dict__.copy()

    @staticmethod
    def from_dict(d: dict) -> "Admin":
        return Admin(**d)
