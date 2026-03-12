"""
models/poll.py
Poll and PollPosition domain models.
"""
from dataclasses import dataclass, field
from typing import List


@dataclass
class PollPosition:
    position_id: int
    position_title: str
    candidate_ids: List[int]
    max_winners: int

    def to_dict(self) -> dict:
        return self.__dict__.copy()

    @staticmethod
    def from_dict(d: dict) -> "PollPosition":
        return PollPosition(**d)


@dataclass
class Poll:
    id: int
    title: str
    description: str
    election_type: str
    start_date: str
    end_date: str
    positions: List[dict]    # stored as raw dicts for JSON round-trip compatibility
    station_ids: List[int]
    status: str              # draft | open | closed
    total_votes_cast: int
    created_at: str
    created_by: str

    def to_dict(self) -> dict:
        return self.__dict__.copy()

    @staticmethod
    def from_dict(d: dict) -> "Poll":
        return Poll(**d)
