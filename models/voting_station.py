"""
models/voting_station.py
VotingStation domain model.
"""
from dataclasses import dataclass


@dataclass
class VotingStation:
    id: int
    name: str
    location: str
    region: str
    capacity: int
    registered_voters: int
    supervisor: str
    contact: str
    opening_time: str
    closing_time: str
    is_active: bool
    created_at: str
    created_by: str

    def to_dict(self) -> dict:
        return self.__dict__.copy()

    @staticmethod
    def from_dict(d: dict) -> "VotingStation":
        return VotingStation(**d)
