"""
utils/validators.py
Centralised validation helpers — eliminates duplicated age/date logic
that existed in both create_candidate() and register_voter() in the monolith.
"""
import datetime

VALID_ELECTION_TYPES = ["General", "Primary", "By-election", "Referendum"]
MIN_CANDIDATE_AGE    = 25
MAX_CANDIDATE_AGE    = 75
MIN_VOTER_AGE        = 18
REQUIRED_EDUCATION_LEVELS = [
    "Bachelor's Degree",
    "Master's Degree",
    "PhD",
    "Doctorate",
]


def parse_date(date_str: str) -> datetime.datetime:
    """Parse YYYY-MM-DD string; raises ValueError on bad format."""
    return datetime.datetime.strptime(date_str.strip(), "%Y-%m-%d")


def calculate_age(dob_str: str) -> int:
    """Return integer age from a YYYY-MM-DD date-of-birth string."""
    dob = parse_date(dob_str)
    return (datetime.datetime.now() - dob).days // 365


def is_valid_election_type(value: str) -> bool:
    return value in VALID_ELECTION_TYPES


def is_valid_level(value: str) -> bool:
    return value.lower() in ["national", "regional", "local"]
