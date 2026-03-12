"""
services/admin_service.py
Admin account management (create, view, deactivate).
Only super_admins may create or deactivate other admins.
"""
import datetime
from data.storage import AppState
from utils.helpers import hash_password, log_action

VALID_ROLES = ["super_admin", "election_officer", "station_manager", "auditor"]


class AdminService:

    def __init__(self, state: AppState):
        self.state = state

    def create(self, data: dict, created_by: str, creator_role: str) -> dict:
        s = self.state
        if creator_role != "super_admin":
            return {"ok": False, "error": "Only super admins can create admin accounts."}
        if not data.get("username"):
            return {"ok": False, "error": "Username cannot be empty."}
        if any(a["username"] == data["username"] for a in s.admins.values()):
            return {"ok": False, "error": "Username already exists."}
        if len(data.get("password", "")) < 6:
            return {"ok": False, "error": "Password must be at least 6 characters."}
        if data.get("role") not in VALID_ROLES:
            return {"ok": False, "error": f"Invalid role. Choose from: {', '.join(VALID_ROLES)}"}

        aid = s.admin_id_counter
        s.admins[aid] = {
            "id": aid,
            "username": data["username"],
            "password": hash_password(data["password"]),
            "full_name": data.get("full_name", ""),
            "email": data.get("email", ""),
            "role": data["role"],
            "created_at": str(datetime.datetime.now()),
            "is_active": True,
        }
        log_action(s, "CREATE_ADMIN", created_by, f"Created admin: {data['username']} (Role: {data['role']})")
        s.admin_id_counter += 1
        s.save()
        return {"ok": True, "id": aid}

    def deactivate(self, aid: int, deactivated_by: str, current_admin_id: int, actor_role: str) -> dict:
        s = self.state
        if actor_role != "super_admin":
            return {"ok": False, "error": "Only super admins can deactivate admin accounts."}
        if aid not in s.admins:
            return {"ok": False, "error": "Admin not found."}
        if aid == current_admin_id:
            return {"ok": False, "error": "Cannot deactivate your own account."}
        username = s.admins[aid]["username"]
        s.admins[aid]["is_active"] = False
        log_action(s, "DEACTIVATE_ADMIN", deactivated_by, f"Deactivated admin: {username}")
        s.save()
        return {"ok": True, "username": username}
