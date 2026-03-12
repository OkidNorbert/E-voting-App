"""
models/position.py
Position domain model.
"""
from dataclasses import dataclass


@dataclass
class Position:
    id: int
    title: str
    description: str
    level: str          # National | Regional | Local
    max_winners: int
    min_candidate_age: int
    is_active: bool
    created_at: str
    created_by: str

    def to_dict(self) -> dict:
        return self.__dict__.copy()

    @staticmethod
    def from_dict(d: dict) -> "Position":
        return Position(**d)
