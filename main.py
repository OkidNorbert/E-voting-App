"""
main.py
Clean entry point for the refactored E-Voting System.
Loads data, invokes login UI, and routes to respective dashboards.
"""
from data.storage import AppState
from ui.login_ui import show_login_menu
from ui.admin_ui import AdminUI
from ui.voter_ui import VoterUI
from utils.colors import THEME_LOGIN, RESET
import time


def main():
    print(f"\n  {THEME_LOGIN}Loading Refactored E-Voting System...{RESET}")
    
    state = AppState()
    state.load()
    time.sleep(0.5)

    while True:
        user, role = show_login_menu(state)
        
        if user is None:
            # Clean exit selected
            break
            
        if role == "admin":
            dashboard = AdminUI(state, user)
            dashboard.run_dashboard()
        elif role == "voter":
            dashboard = VoterUI(state, user)
            dashboard.run_dashboard()

if __name__ == "__main__":
    main()
