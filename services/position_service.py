"""
services/position_service.py
CRUD for election positions.
Enforces the age-cap consistency rule: min_candidate_age must be
within [MIN_CANDIDATE_AGE, MAX_CANDIDATE_AGE] so no impossible
position can be created.
"""
import datetime
from data.storage import AppState
from utils.helpers import log_action
from utils.validators import MIN_CANDIDATE_AGE, MAX_CANDIDATE_AGE, is_valid_level


class PositionService:

    def __init__(self, state: AppState):
        self.state = state

    def create(self, data: dict, created_by: str) -> dict:
        s = self.state
        if not data.get("title"):
            return {"ok": False, "error": "Position title cannot be empty."}
        if not is_valid_level(data.get("level", "")):
            return {"ok": False, "error": "Level must be National, Regional, or Local."}
        try:
            max_winners = int(data.get("max_winners", 0))
            if max_winners <= 0:
                return {"ok": False, "error": "Must be at least 1 winner/seat."}
        except (ValueError, TypeError):
            return {"ok": False, "error": "Invalid number of winners."}

        # ── Age cap fix — prevents impossible positions ────────
        try:
            min_age = int(data.get("min_candidate_age", MIN_CANDIDATE_AGE))
        except (ValueError, TypeError):
            min_age = MIN_CANDIDATE_AGE
        if not (MIN_CANDIDATE_AGE <= min_age <= MAX_CANDIDATE_AGE):
            return {
                "ok": False,
                "error": (
                    f"Minimum candidate age must be between "
                    f"{MIN_CANDIDATE_AGE} and {MAX_CANDIDATE_AGE}. "
                    f"Candidates older than {MAX_CANDIDATE_AGE} are ineligible."
                ),
            }

        pid = s.position_id_counter
        s.positions[pid] = {
            "id": pid,
            "title": data["title"],
            "description": data.get("description", ""),
            "level": data["level"].capitalize(),
            "max_winners": max_winners,
            "min_candidate_age": min_age,
            "is_active": True,
            "created_at": str(datetime.datetime.now()),
            "created_by": created_by,
        }
        log_action(s, "CREATE_POSITION", created_by, f"Created position: {data['title']} (ID: {pid})")
        s.position_id_counter += 1
        s.save()
        return {"ok": True, "id": pid}

    def update(self, pid: int, data: dict, updated_by: str) -> dict:
        s = self.state
        if pid not in s.positions:
            return {"ok": False, "error": "Position not found."}
        p = s.positions[pid]
        if data.get("title"):
            p["title"] = data["title"]
        if data.get("description"):
            p["description"] = data["description"]
        if data.get("level") and is_valid_level(data["level"]):
            p["level"] = data["level"].capitalize()
        if data.get("max_winners"):
            try:
                p["max_winners"] = int(data["max_winners"])
            except ValueError:
                pass
        log_action(s, "UPDATE_POSITION", updated_by, f"Updated position: {p['title']}")
        s.save()
        return {"ok": True}

    def deactivate(self, pid: int, deleted_by: str) -> dict:
        s = self.state
        if pid not in s.positions:
            return {"ok": False, "error": "Position not found."}
        for poll in s.polls.values():
            for pp in poll.get("positions", []):
                if pp["position_id"] == pid and poll["status"] == "open":
                    return {"ok": False, "error": f"Cannot delete — in active poll: {poll['title']}"}
        name = s.positions[pid]["title"]
        s.positions[pid]["is_active"] = False
        log_action(s, "DELETE_POSITION", deleted_by, f"Deactivated position: {name}")
        s.save()
        return {"ok": True}
