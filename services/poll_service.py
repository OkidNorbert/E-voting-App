"""
services/poll_service.py
Poll lifecycle management: create, update, delete, open/close, assign candidates.
"""
import datetime
from data.storage import AppState
from utils.helpers import log_action
from utils.validators import is_valid_election_type, parse_date, MIN_CANDIDATE_AGE


class PollService:

    def __init__(self, state: AppState):
        self.state = state

    def create(self, data: dict, created_by: str) -> dict:
        s = self.state
        if not data.get("title"):
            return {"ok": False, "error": "Title cannot be empty."}
        if not is_valid_election_type(data.get("election_type", "")):
            return {"ok": False, "error": "Invalid election type. Choose: General, Primary, By-election, Referendum."}
        try:
            sd = parse_date(data["start_date"])
            ed = parse_date(data["end_date"])
            if ed <= sd:
                return {"ok": False, "error": "End date must be after start date."}
        except (ValueError, KeyError):
            return {"ok": False, "error": "Invalid date format. Use YYYY-MM-DD."}

        poll_positions = []
        for spid in data.get("position_ids", []):
            if spid in s.positions and s.positions[spid]["is_active"]:
                p = s.positions[spid]
                poll_positions.append({
                    "position_id": spid,
                    "position_title": p["title"],
                    "candidate_ids": [],
                    "max_winners": p["max_winners"],
                })
        if not poll_positions:
            return {"ok": False, "error": "No valid positions selected."}

        selected_stations = data.get("station_ids", [])
        if not selected_stations:
            return {"ok": False, "error": "No voting stations selected."}

        pid = s.poll_id_counter
        s.polls[pid] = {
            "id": pid,
            "title": data["title"],
            "description": data.get("description", ""),
            "election_type": data["election_type"],
            "start_date": data["start_date"],
            "end_date": data["end_date"],
            "positions": poll_positions,
            "station_ids": selected_stations,
            "status": "draft",
            "total_votes_cast": 0,
            "created_at": str(datetime.datetime.now()),
            "created_by": created_by,
        }
        log_action(s, "CREATE_POLL", created_by, f"Created poll: {data['title']} (ID: {pid})")
        s.poll_id_counter += 1
        s.save()
        return {"ok": True, "id": pid}

    def update(self, pid: int, data: dict, updated_by: str) -> dict:
        s = self.state
        if pid not in s.polls:
            return {"ok": False, "error": "Poll not found."}
        poll = s.polls[pid]
        if poll["status"] == "open":
            return {"ok": False, "error": "Cannot update an open poll. Close it first."}
        if poll["status"] == "closed" and poll["total_votes_cast"] > 0:
            return {"ok": False, "error": "Cannot update a poll with recorded votes."}
        for field in ("title", "description", "election_type"):
            if data.get(field):
                poll[field] = data[field]
        for date_field in ("start_date", "end_date"):
            if data.get(date_field):
                try:
                    parse_date(data[date_field])
                    poll[date_field] = data[date_field]
                except ValueError:
                    pass
        log_action(s, "UPDATE_POLL", updated_by, f"Updated poll: {poll['title']}")
        s.save()
        return {"ok": True}

    def delete(self, pid: int, deleted_by: str) -> dict:
        s = self.state
        if pid not in s.polls:
            return {"ok": False, "error": "Poll not found."}
        if s.polls[pid]["status"] == "open":
            return {"ok": False, "error": "Cannot delete an open poll. Close it first."}
        title = s.polls[pid]["title"]
        vote_count = s.polls[pid]["total_votes_cast"]
        del s.polls[pid]
        s.votes = [v for v in s.votes if v["poll_id"] != pid]
        log_action(s, "DELETE_POLL", deleted_by, f"Deleted poll: {title}")
        s.save()
        return {"ok": True, "title": title, "had_votes": vote_count > 0}

    def set_status(self, pid: int, new_status: str, changed_by: str) -> dict:
        """Open, close, or reopen a poll."""
        s = self.state
        if pid not in s.polls:
            return {"ok": False, "error": "Poll not found."}
        poll = s.polls[pid]
        if new_status == "open":
            if not any(pos["candidate_ids"] for pos in poll["positions"]):
                return {"ok": False, "error": "Cannot open — no candidates assigned to any position."}
        poll["status"] = new_status
        action = "OPEN_POLL" if new_status == "open" else ("CLOSE_POLL" if new_status == "closed" else "REOPEN_POLL")
        log_action(s, action, changed_by, f"{action}: {poll['title']}")
        s.save()
        return {"ok": True}

    def assign_candidates(self, pid: int, assignments: dict, updated_by: str) -> dict:
        """
        assignments = {position_index: [candidate_id, ...]}
        """
        s = self.state
        if pid not in s.polls:
            return {"ok": False, "error": "Poll not found."}
        poll = s.polls[pid]
        if poll["status"] == "open":
            return {"ok": False, "error": "Cannot modify candidates of an open poll."}
        for idx, cand_ids in assignments.items():
            if 0 <= idx < len(poll["positions"]):
                poll["positions"][idx]["candidate_ids"] = cand_ids
        log_action(s, "ASSIGN_CANDIDATES", updated_by, f"Updated candidates for poll: {poll['title']}")
        s.save()
        return {"ok": True}
