"""
models/vote.py
Vote domain model.
"""
from dataclasses import dataclass


@dataclass
class Vote:
    vote_id: str
    poll_id: int
    position_id: int
    candidate_id: object   # int or None (abstain)
    voter_id: int
    station_id: int
    timestamp: str
    abstained: bool

    def to_dict(self) -> dict:
        return self.__dict__.copy()

    @staticmethod
    def from_dict(d: dict) -> "Vote":
        return Vote(**d)
