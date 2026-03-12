"""
services/candidate_service.py
CRUD operations and eligibility enforcement for candidates.
"""
import datetime
from data.storage import AppState
from utils.helpers import hash_password, log_action
from utils.validators import (
    calculate_age, MIN_CANDIDATE_AGE, MAX_CANDIDATE_AGE, REQUIRED_EDUCATION_LEVELS
)


class CandidateService:

    def __init__(self, state: AppState):
        self.state = state

    def create(self, data: dict, created_by: str) -> dict:
        s = self.state
        if not data.get("full_name"):
            return {"ok": False, "error": "Name cannot be empty."}
        if not data.get("national_id"):
            return {"ok": False, "error": "National ID cannot be empty."}
        if any(c["national_id"] == data["national_id"] for c in s.candidates.values()):
            return {"ok": False, "error": "A candidate with this National ID already exists."}
        try:
            age = calculate_age(data["date_of_birth"])
        except ValueError:
            return {"ok": False, "error": "Invalid date format. Use YYYY-MM-DD."}
        if age < MIN_CANDIDATE_AGE:
            return {"ok": False, "error": f"Candidate must be at least {MIN_CANDIDATE_AGE} years old. Current age: {age}"}
        if age > MAX_CANDIDATE_AGE:
            return {"ok": False, "error": f"Candidate must not be older than {MAX_CANDIDATE_AGE}. Current age: {age}"}
        if data.get("criminal_record", "no").lower() == "yes":
            log_action(s, "CANDIDATE_REJECTED", created_by, f"Candidate {data['full_name']} rejected - criminal record")
            return {"ok": False, "error": "Candidates with criminal records are not eligible."}
        if data.get("education") not in REQUIRED_EDUCATION_LEVELS:
            return {"ok": False, "error": "Invalid education level."}

        cid = s.candidate_id_counter
        s.candidates[cid] = {
            "id": cid,
            "full_name": data["full_name"],
            "national_id": data["national_id"],
            "date_of_birth": data["date_of_birth"],
            "age": age,
            "gender": data.get("gender", ""),
            "education": data["education"],
            "party": data.get("party", ""),
            "manifesto": data.get("manifesto", ""),
            "address": data.get("address", ""),
            "phone": data.get("phone", ""),
            "email": data.get("email", ""),
            "has_criminal_record": False,
            "years_experience": int(data.get("years_experience", 0)),
            "is_active": True,
            "is_approved": True,
            "created_at": str(datetime.datetime.now()),
            "created_by": created_by,
        }
        log_action(s, "CREATE_CANDIDATE", created_by, f"Created candidate: {data['full_name']} (ID: {cid})")
        s.candidate_id_counter += 1
        s.save()
        return {"ok": True, "id": cid}

    def update(self, cid: int, data: dict, updated_by: str) -> dict:
        s = self.state
        if cid not in s.candidates:
            return {"ok": False, "error": "Candidate not found."}
        c = s.candidates[cid]
        for field in ("full_name", "party", "manifesto", "phone", "email", "address"):
            if data.get(field):
                c[field] = data[field]
        if data.get("years_experience") is not None:
            try:
                c["years_experience"] = int(data["years_experience"])
            except ValueError:
                pass
        log_action(s, "UPDATE_CANDIDATE", updated_by, f"Updated candidate: {c['full_name']} (ID: {cid})")
        s.save()
        return {"ok": True}

    def deactivate(self, cid: int, deleted_by: str) -> dict:
        s = self.state
        if cid not in s.candidates:
            return {"ok": False, "error": "Candidate not found."}
        # Block deletion if in an open poll
        for poll in s.polls.values():
            if poll["status"] == "open":
                for pos in poll.get("positions", []):
                    if cid in pos.get("candidate_ids", []):
                        return {"ok": False, "error": f"Cannot delete — candidate is in active poll: {poll['title']}"}
        name = s.candidates[cid]["full_name"]
        s.candidates[cid]["is_active"] = False
        log_action(s, "DELETE_CANDIDATE", deleted_by, f"Deactivated candidate: {name} (ID: {cid})")
        s.save()
        return {"ok": True, "name": name}

    def search(self, by: str, term) -> list:
        s = self.state
        if by == "name":
            return [c for c in s.candidates.values() if term.lower() in c["full_name"].lower()]
        if by == "party":
            return [c for c in s.candidates.values() if term.lower() in c["party"].lower()]
        if by == "education":
            return [c for c in s.candidates.values() if c["education"] == term]
        if by == "age_range":
            mn, mx = term
            return [c for c in s.candidates.values() if mn <= c["age"] <= mx]
        return []
