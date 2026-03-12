"""
ui/voter_ui.py
Voter Dashboard Presentation Layer.
"""
from utils.colors import (
    header, subheader, menu_item, prompt, error, success, info, warning,
    THEME_VOTER, THEME_VOTER_ACCENT, DIM, RESET, BOLD, GRAY, BRIGHT_GREEN
)
from utils.helpers import clear_screen, pause
from data.storage import AppState
from services.vote_service import VoteService
from services.report_service import ReportService
from utils.helpers import hash_password

class VoterUI:
    def __init__(self, state: AppState, current_user: dict):
        self.state = state
        self.user = current_user
        self.vote_svc = VoteService(state)
        self.rpt_svc = ReportService(state)

    def run_dashboard(self):
        while True:
            clear_screen()
            header("VOTER DASHBOARD", THEME_VOTER)
            station_name = self.state.voting_stations.get(self.user["station_id"], {}).get("name", "Unknown")
            print(f"  {THEME_VOTER}  ● {RESET}{BOLD}{self.user['full_name']}{RESET}")
            print(f"  {DIM}    Card: {self.user['voter_card_number']}  │  Station: {station_name}{RESET}\n")

            menu_item(1, "View Open Polls", THEME_VOTER)
            menu_item(2, "Cast Vote", THEME_VOTER)
            menu_item(3, "View My Voting History", THEME_VOTER)
            menu_item(4, "View Results (Closed Polls)", THEME_VOTER)
            menu_item(5, "View My Profile", THEME_VOTER)
            menu_item(6, "Logout", THEME_VOTER)
            print()
            choice = prompt("Enter choice: ")

            if choice == "1": self.ui_view_open_polls()
            elif choice == "2": self.ui_cast_vote()
            elif choice == "3": self.ui_view_history()
            elif choice == "4": self.ui_view_results()
            elif choice == "5": self.ui_profile()
            elif choice == "6": self.state.save(); break
            else: error("Invalid choice."); pause()

    def ui_view_open_polls(self):
        clear_screen(); header("OPEN POLLS", THEME_VOTER)
        open_polls = [p for p in self.state.polls.values() if p["status"] == "open"]
        if not open_polls: info("No open polls."); pause(); return
        for p in open_polls:
            print(f"\n  {BOLD}{THEME_VOTER}Poll #{p['id']}: {p['title']}{RESET}")
            for pos in p["positions"]:
                cnames = [self.state.candidates[cid]["full_name"] for cid in pos["candidate_ids"] if cid in self.state.candidates]
                print(f"    {THEME_VOTER_ACCENT}▸{RESET} {pos['position_title']}: {', '.join(cnames)}")
        pause()

    def ui_cast_vote(self):
        clear_screen(); header("CAST YOUR VOTE", THEME_VOTER)
        available = [p for p in self.state.polls.values() if p["status"] == "open" and self.user["station_id"] in p["station_ids"] and p["id"] not in self.user.get("has_voted_in", [])]
        if not available: info("No available polls to vote in."); pause(); return
        for p in available: print(f"  {THEME_VOTER}{p['id']}.{RESET} {p['title']}")
        try: pid = int(prompt("\nSelect Poll ID: "))
        except ValueError: return
        poll = next((p for p in available if p["id"] == pid), None)
        if not poll: return

        print(); header(f"Voting: {poll['title']}", THEME_VOTER)
        selections = []
        for pos in poll["positions"]:
            subheader(pos["position_title"], THEME_VOTER_ACCENT)
            if not pos["candidate_ids"]: info("No candidates."); continue
            valid_cids = []
            for idx, cid in enumerate(pos["candidate_ids"], 1):
                c = self.state.candidates.get(cid)
                if c:
                    valid_cids.append(cid)
                    print(f"    {THEME_VOTER}{BOLD}{len(valid_cids)}.{RESET} {c['full_name']} {DIM}({c['party']}){RESET}")
            print(f"    {GRAY}{BOLD}0.{RESET} {GRAY}Abstain{RESET}")
            
            try: choice = int(prompt(f"Choice for {pos['position_title']}: "))
            except ValueError: choice = 0
            
            if choice == 0 or choice > len(valid_cids):
                selections.append({"position_id": pos["position_id"], "position_title": pos["position_title"], "candidate_id": None, "abstained": True})
            else:
                c_id = valid_cids[choice - 1]
                selections.append({"position_id": pos["position_id"], "position_title": pos["position_title"], "candidate_id": c_id, "abstained": False})
        
        if prompt("\nConfirm votes? (yes/no): ").lower() == "yes":
            res = self.vote_svc.cast(self.user, pid, selections)
            if res["ok"]: success("Vote recorded!"); print(f"  Hash: {res['vote_hash']}")
            else: error(res["error"])
        pause()

    def ui_view_history(self):
        clear_screen(); header("VOTING HISTORY", THEME_VOTER)
        for pid in self.user.get("has_voted_in", []):
            title = self.state.polls.get(pid, {}).get("title", f"Poll #{pid}")
            print(f"  {BRIGHT_GREEN}✔ Voted in:{RESET} {title}")
        pause()

    def ui_view_results(self):
        clear_screen(); header("RESULTS", THEME_VOTER)
        closed_polls = [p for p in self.state.polls.values() if p["status"] == "closed"]
        if not closed_polls: info("No closed polls."); pause(); return
        for p in closed_polls: print(f"  - {p['title']} (ID: {p['id']})")
        pause()

    def ui_profile(self):
        clear_screen(); header("MY PROFILE", THEME_VOTER)
        v = self.user
        print(f"  Name: {v['full_name']}\n  Card: {v['voter_card_number']}")
        pause()
