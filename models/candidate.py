"""
models/candidate.py
Candidate domain model.
"""
from dataclasses import dataclass, field


@dataclass
class Candidate:
    id: int
    full_name: str
    national_id: str
    date_of_birth: str
    age: int
    gender: str
    education: str
    party: str
    manifesto: str
    address: str
    phone: str
    email: str
    has_criminal_record: bool
    years_experience: int
    is_active: bool
    is_approved: bool
    created_at: str
    created_by: str

    def to_dict(self) -> dict:
        return self.__dict__.copy()

    @staticmethod
    def from_dict(d: dict) -> "Candidate":
        return Candidate(**d)
