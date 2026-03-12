"""
models/voter.py
Voter domain model.
"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class Voter:
    id: int
    full_name: str
    national_id: str
    date_of_birth: str
    age: int
    gender: str
    address: str
    phone: str
    email: str
    password: str
    voter_card_number: str
    station_id: int
    is_verified: bool
    is_active: bool
    has_voted_in: List[int]
    registered_at: str
    role: str = "voter"

    def to_dict(self) -> dict:
        return self.__dict__.copy()

    @staticmethod
    def from_dict(d: dict) -> "Voter":
        return Voter(**d)
