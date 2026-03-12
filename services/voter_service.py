"""
services/voter_service.py
Voter management operations for admin use: view, verify, deactivate, search.
"""
from data.storage import AppState
from utils.helpers import log_action


class VoterService:

    def __init__(self, state: AppState):
        self.state = state

    def verify(self, vid: int, verified_by: str) -> dict:
        s = self.state
        if vid not in s.voters:
            return {"ok": False, "error": "Voter not found."}
        if s.voters[vid]["is_verified"]:
            return {"ok": False, "error": "Voter is already verified."}
        s.voters[vid]["is_verified"] = True
        log_action(s, "VERIFY_VOTER", verified_by, f"Verified voter: {s.voters[vid]['full_name']}")
        s.save()
        return {"ok": True, "name": s.voters[vid]["full_name"]}

    def verify_all(self, verified_by: str) -> int:
        s = self.state
        count = 0
        for v in s.voters.values():
            if not v["is_verified"]:
                v["is_verified"] = True
                count += 1
        log_action(s, "VERIFY_ALL_VOTERS", verified_by, f"Bulk verified {count} voters")
        s.save()
        return count

    def deactivate(self, vid: int, deactivated_by: str) -> dict:
        s = self.state
        if vid not in s.voters:
            return {"ok": False, "error": "Voter not found."}
        if not s.voters[vid]["is_active"]:
            return {"ok": False, "error": "Voter is already deactivated."}
        name = s.voters[vid]["full_name"]
        s.voters[vid]["is_active"] = False
        log_action(s, "DEACTIVATE_VOTER", deactivated_by, f"Deactivated voter: {name}")
        s.save()
        return {"ok": True, "name": name}

    def search(self, by: str, term) -> list:
        s = self.state
        if by == "name":
            return [v for v in s.voters.values() if term.lower() in v["full_name"].lower()]
        if by == "card":
            return [v for v in s.voters.values() if v["voter_card_number"] == term]
        if by == "national_id":
            return [v for v in s.voters.values() if v["national_id"] == term]
        if by == "station":
            return [v for v in s.voters.values() if v["station_id"] == term]
        return []
