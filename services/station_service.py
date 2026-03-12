"""
services/station_service.py
CRUD operations for voting stations.
"""
import datetime
from data.storage import AppState
from utils.helpers import log_action


class StationService:

    def __init__(self, state: AppState):
        self.state = state

    def create(self, data: dict, created_by: str) -> dict:
        s = self.state
        if not data.get("name"):
            return {"ok": False, "error": "Station name cannot be empty."}
        if not data.get("location"):
            return {"ok": False, "error": "Location cannot be empty."}
        try:
            capacity = int(data.get("capacity", 0))
            if capacity <= 0:
                return {"ok": False, "error": "Capacity must be a positive number."}
        except (ValueError, TypeError):
            return {"ok": False, "error": "Invalid capacity."}

        sid = s.station_id_counter
        s.voting_stations[sid] = {
            "id": sid,
            "name": data["name"],
            "location": data["location"],
            "region": data.get("region", ""),
            "capacity": capacity,
            "registered_voters": 0,
            "supervisor": data.get("supervisor", ""),
            "contact": data.get("contact", ""),
            "opening_time": data.get("opening_time", ""),
            "closing_time": data.get("closing_time", ""),
            "is_active": True,
            "created_at": str(datetime.datetime.now()),
            "created_by": created_by,
        }
        log_action(s, "CREATE_STATION", created_by, f"Created station: {data['name']} (ID: {sid})")
        s.station_id_counter += 1
        s.save()
        return {"ok": True, "id": sid}

    def update(self, sid: int, data: dict, updated_by: str) -> dict:
        s = self.state
        if sid not in s.voting_stations:
            return {"ok": False, "error": "Station not found."}
        st = s.voting_stations[sid]
        for field in ("name", "location", "region", "supervisor", "contact"):
            if data.get(field):
                st[field] = data[field]
        if data.get("capacity"):
            try:
                st["capacity"] = int(data["capacity"])
            except ValueError:
                pass
        log_action(s, "UPDATE_STATION", updated_by, f"Updated station: {st['name']} (ID: {sid})")
        s.save()
        return {"ok": True}

    def deactivate(self, sid: int, deleted_by: str, force: bool = False) -> dict:
        s = self.state
        if sid not in s.voting_stations:
            return {"ok": False, "error": "Station not found."}
        voter_count = sum(1 for v in s.voters.values() if v["station_id"] == sid)
        if voter_count > 0 and not force:
            return {"ok": False, "needs_confirm": True, "voter_count": voter_count}
        name = s.voting_stations[sid]["name"]
        s.voting_stations[sid]["is_active"] = False
        log_action(s, "DELETE_STATION", deleted_by, f"Deactivated station: {name}")
        s.save()
        return {"ok": True, "name": name}

    def voter_count(self, sid: int) -> int:
        return sum(1 for v in self.state.voters.values() if v["station_id"] == sid)
