"""
services/auth_service.py
Handles login authentication and voter self-registration.
No UI calls — all presentation is done by the caller (ui layer).
"""
import datetime
from data.storage import AppState
from utils.helpers import hash_password, generate_voter_card_number, log_action
from utils.validators import calculate_age, MIN_VOTER_AGE


class AuthService:

    def __init__(self, state: AppState):
        self.state = state

    # ── Admin login ───────────────────────────────────────────

    def login_admin(self, username: str, password: str) -> dict | None:
        """Return admin dict if credentials match, else None."""
        hashed = hash_password(password)
        for admin in self.state.admins.values():
            if admin["username"] == username and admin["password"] == hashed:
                if not admin["is_active"]:
                    return "deactivated"
                log_action(self.state, "LOGIN", username, "Admin login successful")
                return admin
        log_action(self.state, "LOGIN_FAILED", username, "Invalid admin credentials")
        return None

    # ── Voter login ───────────────────────────────────────────

    def login_voter(self, voter_card: str, password: str) -> dict | str | None:
        """
        Returns:
            dict         — voter record on success
            'deactivated'— account inactive
            'unverified' — pending admin verification
            None         — wrong credentials
        """
        hashed = hash_password(password)
        for voter in self.state.voters.values():
            if voter["voter_card_number"] == voter_card and voter["password"] == hashed:
                if not voter["is_active"]:
                    log_action(self.state, "LOGIN_FAILED", voter_card, "Voter account deactivated")
                    return "deactivated"
                if not voter["is_verified"]:
                    log_action(self.state, "LOGIN_FAILED", voter_card, "Voter not verified")
                    return "unverified"
                log_action(self.state, "LOGIN", voter_card, "Voter login successful")
                return voter
        log_action(self.state, "LOGIN_FAILED", voter_card, "Invalid voter credentials")
        return None

    # ── Voter registration ────────────────────────────────────

    def register_voter(self, data: dict) -> dict:
        """
        Validates and creates a new voter record.
        Returns {'ok': True, 'voter_card': ...} or {'ok': False, 'error': ...}.
        """
        s = self.state

        if not data.get("full_name"):
            return {"ok": False, "error": "Name cannot be empty."}
        if not data.get("national_id"):
            return {"ok": False, "error": "National ID cannot be empty."}
        if any(v["national_id"] == data["national_id"] for v in s.voters.values()):
            return {"ok": False, "error": "A voter with this National ID already exists."}

        try:
            age = calculate_age(data["date_of_birth"])
        except ValueError:
            return {"ok": False, "error": "Invalid date format. Use YYYY-MM-DD."}
        if age < MIN_VOTER_AGE:
            return {"ok": False, "error": f"You must be at least {MIN_VOTER_AGE} years old to register."}

        if data.get("gender", "").upper() not in ["M", "F", "OTHER"]:
            return {"ok": False, "error": "Invalid gender selection."}
        if len(data.get("password", "")) < 6:
            return {"ok": False, "error": "Password must be at least 6 characters."}
        if data["password"] != data.get("confirm_password", ""):
            return {"ok": False, "error": "Passwords do not match."}

        station_id = data.get("station_id")
        if station_id not in s.voting_stations or not s.voting_stations[station_id]["is_active"]:
            return {"ok": False, "error": "Invalid station selection."}

        voter_card = generate_voter_card_number()
        s.voters[s.voter_id_counter] = {
            "id": s.voter_id_counter,
            "full_name": data["full_name"],
            "national_id": data["national_id"],
            "date_of_birth": data["date_of_birth"],
            "age": age,
            "gender": data["gender"].upper(),
            "address": data.get("address", ""),
            "phone": data.get("phone", ""),
            "email": data.get("email", ""),
            "password": hash_password(data["password"]),
            "voter_card_number": voter_card,
            "station_id": station_id,
            "is_verified": False,
            "is_active": True,
            "has_voted_in": [],
            "registered_at": str(datetime.datetime.now()),
            "role": "voter",
        }
        log_action(s, "REGISTER", data["full_name"], f"New voter registered with card: {voter_card}")
        s.voter_id_counter += 1
        s.save()
        return {"ok": True, "voter_card": voter_card}
