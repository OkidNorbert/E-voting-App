"""
services/report_service.py
Read-only queries for results, statistics, and audit log.
Returns plain Python dicts/lists — formatting is done by the UI layer.
"""
from data.storage import AppState


class ReportService:

    def __init__(self, state: AppState):
        self.state = state

    # ── Poll results ──────────────────────────────────────────

    def poll_results(self, poll_id: int) -> dict:
        """Returns vote counts per position, turnout, and eligible voter count."""
        s = self.state
        if poll_id not in s.polls:
            return {}
        poll = s.polls[poll_id]
        eligible = sum(
            1 for v in s.voters.values()
            if v["is_verified"] and v["is_active"] and v["station_id"] in poll["station_ids"]
        )
        turnout = (poll["total_votes_cast"] / eligible * 100) if eligible > 0 else 0

        positions_result = []
        for pos in poll["positions"]:
            vote_counts = {}
            abstain_count = 0
            total_pos = 0
            for v in s.votes:
                if v["poll_id"] == poll_id and v["position_id"] == pos["position_id"]:
                    total_pos += 1
                    if v["abstained"]:
                        abstain_count += 1
                    else:
                        cid = v["candidate_id"]
                        vote_counts[cid] = vote_counts.get(cid, 0) + 1
            positions_result.append({
                "position_title": pos["position_title"],
                "max_winners":    pos["max_winners"],
                "vote_counts":    vote_counts,
                "abstain_count":  abstain_count,
                "total_pos":      total_pos,
                "candidates":     s.candidates,
            })

        return {
            "poll": poll,
            "eligible": eligible,
            "turnout": turnout,
            "positions": positions_result,
        }

    # ── Station-wise results ──────────────────────────────────

    def station_results(self, poll_id: int) -> list:
        s = self.state
        if poll_id not in s.polls:
            return []
        poll = s.polls[poll_id]
        results = []
        for sid in poll["station_ids"]:
            if sid not in s.voting_stations:
                continue
            station = s.voting_stations[sid]
            station_votes = [v for v in s.votes if v["poll_id"] == poll_id and v["station_id"] == sid]
            voted = len(set(v["voter_id"] for v in station_votes))
            registered = sum(1 for v in s.voters.values()
                             if v["station_id"] == sid and v["is_verified"] and v["is_active"])
            turnout = (voted / registered * 100) if registered > 0 else 0

            pos_data = []
            for pos in poll["positions"]:
                pv = [v for v in station_votes if v["position_id"] == pos["position_id"]]
                vc = {}
                ac = 0
                for v in pv:
                    if v["abstained"]:
                        ac += 1
                    else:
                        vc[v["candidate_id"]] = vc.get(v["candidate_id"], 0) + 1
                pos_data.append({
                    "title": pos["position_title"],
                    "vote_counts": vc,
                    "abstain_count": ac,
                    "candidates": s.candidates,
                })
            results.append({
                "station": station,
                "registered": registered,
                "voted": voted,
                "turnout": turnout,
                "positions": pos_data,
            })
        return results

    # ── Detailed statistics ───────────────────────────────────

    def system_statistics(self) -> dict:
        s = self.state
        candidates = s.candidates
        voters     = s.voters
        stations   = s.voting_stations
        polls      = s.polls

        gender_counts = {}
        age_groups = {"18-25": 0, "26-35": 0, "36-45": 0, "46-55": 0, "56-65": 0, "65+": 0}
        for v in voters.values():
            g = v.get("gender", "?")
            gender_counts[g] = gender_counts.get(g, 0) + 1
            age = v.get("age", 0)
            if age <= 25:   age_groups["18-25"] += 1
            elif age <= 35: age_groups["26-35"] += 1
            elif age <= 45: age_groups["36-45"] += 1
            elif age <= 55: age_groups["46-55"] += 1
            elif age <= 65: age_groups["56-65"] += 1
            else:           age_groups["65+"] += 1

        party_counts = {}
        edu_counts   = {}
        for c in candidates.values():
            if c["is_active"]:
                party_counts[c["party"]] = party_counts.get(c["party"], 0) + 1
                edu_counts[c["education"]] = edu_counts.get(c["education"], 0) + 1

        station_load = []
        for sid, st in stations.items():
            vc = sum(1 for v in voters.values() if v["station_id"] == sid)
            lp = (vc / st["capacity"] * 100) if st["capacity"] > 0 else 0
            station_load.append({"station": st, "voter_count": vc, "load_pct": lp})

        return {
            "candidates": {"total": len(candidates), "active": sum(1 for c in candidates.values() if c["is_active"])},
            "voters":     {"total": len(voters), "verified": sum(1 for v in voters.values() if v["is_verified"]), "active": sum(1 for v in voters.values() if v["is_active"])},
            "stations":   {"total": len(stations), "active": sum(1 for s in stations.values() if s["is_active"])},
            "polls":      {"total": len(polls), "open": sum(1 for p in polls.values() if p["status"] == "open"), "closed": sum(1 for p in polls.values() if p["status"] == "closed"), "draft": sum(1 for p in polls.values() if p["status"] == "draft")},
            "total_votes": len(s.votes),
            "gender_counts": gender_counts,
            "age_groups":    age_groups,
            "party_counts":  party_counts,
            "edu_counts":    edu_counts,
            "station_load":  station_load,
            "voter_total":   len(voters),
        }

    # ── Audit log ─────────────────────────────────────────────

    def audit_entries(self, filter_by: str = "recent", term: str = "") -> list:
        log = self.state.audit_log
        if filter_by == "recent":
            return log[-20:]
        if filter_by == "action" and term:
            return [e for e in log if e["action"] == term]
        if filter_by == "user" and term:
            return [e for e in log if term.lower() in e["user"].lower()]
        return log

    def audit_action_types(self) -> list:
        return list(set(e["action"] for e in self.state.audit_log))
