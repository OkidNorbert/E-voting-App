"""
data/storage.py
Single source of truth for all in-memory application state.
AppState holds every collection and the ID counters.
save() and load() handle JSON persistence — keeping data layer
completely separate from business logic and UI.
"""
import json
import os
import datetime
import hashlib


DATA_FILE = "evoting_data.json"


class AppState:
    """Holds all in-memory collections and auto-increment counters."""

    def __init__(self):
        self.candidates: dict          = {}
        self.candidate_id_counter: int = 1
        self.voting_stations: dict     = {}
        self.station_id_counter: int   = 1
        self.polls: dict               = {}
        self.poll_id_counter: int      = 1
        self.positions: dict           = {}
        self.position_id_counter: int  = 1
        self.voters: dict              = {}
        self.voter_id_counter: int     = 1
        self.admins: dict              = {}
        self.admin_id_counter: int     = 1
        self.votes: list               = []
        self.audit_log: list           = []

        # Seed default super-admin
        self.admins[1] = {
            "id": 1,
            "username": "admin",
            "password": hashlib.sha256("admin123".encode()).hexdigest(),
            "full_name": "System Administrator",
            "email": "admin@evote.com",
            "role": "super_admin",
            "created_at": str(datetime.datetime.now()),
            "is_active": True,
        }
        self.admin_id_counter = 2

    # ── Persistence ────────────────────────────────────────────

    def save(self, path: str = DATA_FILE) -> None:
        payload = {
            "candidates":            self.candidates,
            "candidate_id_counter":  self.candidate_id_counter,
            "voting_stations":       self.voting_stations,
            "station_id_counter":    self.station_id_counter,
            "polls":                 self.polls,
            "poll_id_counter":       self.poll_id_counter,
            "positions":             self.positions,
            "position_id_counter":   self.position_id_counter,
            "voters":                self.voters,
            "voter_id_counter":      self.voter_id_counter,
            "admins":                self.admins,
            "admin_id_counter":      self.admin_id_counter,
            "votes":                 self.votes,
            "audit_log":             self.audit_log,
        }
        try:
            with open(path, "w") as f:
                json.dump(payload, f, indent=2)
        except Exception as e:
            print(f"  Error saving data: {e}")

    def load(self, path: str = DATA_FILE) -> None:
        if not os.path.exists(path):
            return
        try:
            with open(path, "r") as f:
                data = json.load(f)
            self.candidates           = {int(k): v for k, v in data.get("candidates", {}).items()}
            self.candidate_id_counter = data.get("candidate_id_counter", 1)
            self.voting_stations      = {int(k): v for k, v in data.get("voting_stations", {}).items()}
            self.station_id_counter   = data.get("station_id_counter", 1)
            self.polls                = {int(k): v for k, v in data.get("polls", {}).items()}
            self.poll_id_counter      = data.get("poll_id_counter", 1)
            self.positions            = {int(k): v for k, v in data.get("positions", {}).items()}
            self.position_id_counter  = data.get("position_id_counter", 1)
            self.voters               = {int(k): v for k, v in data.get("voters", {}).items()}
            self.voter_id_counter     = data.get("voter_id_counter", 1)
            self.admins               = {int(k): v for k, v in data.get("admins", {}).items()}
            self.admin_id_counter     = data.get("admin_id_counter", 1)
            self.votes                = data.get("votes", [])
            self.audit_log            = data.get("audit_log", [])
        except Exception as e:
            print(f"  Error loading data: {e}")
