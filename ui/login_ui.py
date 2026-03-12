"""
ui/login_ui.py
Presentation layer for login menus and voter registration.
"""
from utils.colors import (
    app_banner, panel, header, subheader, menu_item, error, success, warning, info,
    prompt, masked_input, THEME_LOGIN, THEME_ADMIN, THEME_VOTER, THEME_VOTER_ACCENT,
    BRIGHT_BLUE, DIM, RESET, BRIGHT_YELLOW, BOLD
)
from utils.helpers import clear_screen, pause
from services.auth_service import AuthService
from data.storage import AppState


def show_login_menu(state: AppState) -> tuple[dict, str] | tuple[None, None]:
    """Runs the main login loop. Returns (user_dict, role_string)."""
    auth = AuthService(state)

    while True:
        clear_screen()
        app_banner()
        panel("       Welcome to the secure digital voting platform.\n       Please select an option below.", THEME_LOGIN)
        print()
        menu_item(1, "Login as Admin", THEME_LOGIN)
        menu_item(2, "Login as Voter", THEME_LOGIN)
        menu_item(3, "Register as Voter", THEME_LOGIN)
        menu_item(4, "Exit", THEME_LOGIN)
        print()
        choice = prompt("Enter choice: ")

        if choice == "1":
            clear_screen()
            header("ADMIN LOGIN", THEME_ADMIN)
            print()
            username = prompt("Username: ")
            password = masked_input("Password: ").strip()

            admin = auth.login_admin(username, password)
            if admin == "deactivated":
                error("This account has been deactivated.")
                pause()
            elif isinstance(admin, dict):
                print()
                success(f"Welcome, {admin['full_name']}!")
                pause()
                return admin, "admin"
            else:
                error("Invalid credentials.")
                pause()

        elif choice == "2":
            clear_screen()
            header("VOTER LOGIN", THEME_VOTER)
            print()
            voter_card = prompt("Voter Card Number: ")
            password = masked_input("Password: ").strip()

            voter = auth.login_voter(voter_card, password)
            if voter == "deactivated":
                error("This voter account has been deactivated.")
                pause()
            elif voter == "unverified":
                warning("Your voter registration has not been verified yet.")
                info("Please contact an admin to verify your registration.")
                pause()
            elif isinstance(voter, dict):
                print()
                success(f"Welcome, {voter['full_name']}!")
                pause()
                return voter, "voter"
            else:
                error("Invalid voter card number or password.")
                pause()

        elif choice == "3":
            run_voter_registration(state, auth)

        elif choice == "4":
            print()
            info("Goodbye!")
            state.save()
            return None, None

        else:
            error("Invalid choice.")
            pause()


def run_voter_registration(state: AppState, auth: AuthService) -> None:
    clear_screen()
    header("VOTER REGISTRATION", THEME_VOTER)
    print()

    data = {
        "full_name": prompt("Full Name: "),
        "national_id": prompt("National ID Number: "),
        "date_of_birth": prompt("Date of Birth (YYYY-MM-DD): "),
        "gender": prompt("Gender (M/F/Other): "),
        "address": prompt("Residential Address: "),
        "phone": prompt("Phone Number: "),
        "email": prompt("Email Address: "),
    }
    data["password"] = masked_input("Create Password: ").strip()
    data["confirm_password"] = masked_input("Confirm Password: ").strip()

    if not state.voting_stations:
        error("No voting stations available. Contact admin.")
        pause()
        return

    subheader("Available Voting Stations", THEME_VOTER)
    for sid, station in state.voting_stations.items():
        if station["is_active"]:
            print(f"    {BRIGHT_BLUE}{sid}.{RESET} {station['name']} {DIM}- {station['location']}{RESET}")

    try:
        data["station_id"] = int(prompt("\nSelect your voting station ID: "))
    except ValueError:
        data["station_id"] = -1

    res = auth.register_voter(data)
    if res["ok"]:
        print()
        success("Registration successful!")
        print(f"  {BOLD}Your Voter Card Number: {BRIGHT_YELLOW}{res['voter_card']}{RESET}")
        warning("IMPORTANT: Save this number! You need it to login.")
        info("Your registration is pending admin verification.")
    else:
        error(res["error"])
    pause()
