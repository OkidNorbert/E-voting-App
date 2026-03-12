"""
services/vote_service.py
Ballot casting with duplicate-prevention and vote hashing.
"""
import datetime
import hashlib
from data.storage import AppState
from utils.helpers import log_action


class VoteService:

    def __init__(self, state: AppState):
        self.state = state

    def cast(self, voter: dict, poll_id: int, selections: list) -> dict:
        """
        selections = [
            {"position_id": int, "position_title": str,
             "candidate_id": int|None, "candidate_name": str|None, "abstained": bool}
        ]
        Returns {"ok": True, "vote_hash": str} or {"ok": False, "error": str}
        """
        s = self.state
        if poll_id not in s.polls:
            return {"ok": False, "error": "Poll not found."}
        poll = s.polls[poll_id]
        if poll["status"] != "open":
            return {"ok": False, "error": "This poll is not open."}
        if poll_id in voter.get("has_voted_in", []):
            return {"ok": False, "error": "You have already voted in this poll."}
        if voter["station_id"] not in poll["station_ids"]:
            return {"ok": False, "error": "Your station is not registered for this poll."}

        timestamp = str(datetime.datetime.now())
        vote_hash = hashlib.sha256(
            f"{voter['id']}{poll_id}{timestamp}".encode()
        ).hexdigest()[:16]

        for sel in selections:
            s.votes.append({
                "vote_id":     vote_hash + str(sel["position_id"]),
                "poll_id":     poll_id,
                "position_id": sel["position_id"],
                "candidate_id": sel.get("candidate_id"),
                "voter_id":    voter["id"],
                "station_id":  voter["station_id"],
                "timestamp":   timestamp,
                "abstained":   sel.get("abstained", False),
            })

        # Update voter record (in-memory and persistent)
        voter["has_voted_in"].append(poll_id)
        for v in s.voters.values():
            if v["id"] == voter["id"]:
                v["has_voted_in"].append(poll_id)
                break

        s.polls[poll_id]["total_votes_cast"] += 1
        log_action(s, "CAST_VOTE", voter["voter_card_number"],
                   f"Voted in poll: {poll['title']} (Hash: {vote_hash})")
        s.save()
        return {"ok": True, "vote_hash": vote_hash}
