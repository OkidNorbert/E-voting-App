"""
ui/admin_ui.py
Admin Dashboard Presentation Layer.
Replaces the 32-option if/elif chain with a dispatcher map.
Uses the Services layer for all logic.
"""
from utils.colors import (
    header, subheader, menu_item, prompt, error, success, info, warning,
    table_header, table_divider, status_badge, THEME_ADMIN, THEME_ADMIN_ACCENT,
    DIM, RESET, BOLD, BLACK, GRAY, BG_GREEN
)
from utils.helpers import clear_screen, pause
from data.storage import AppState
from services.candidate_service import CandidateService
from services.station_service import StationService
from services.position_service import PositionService
from services.poll_service import PollService
from services.voter_service import VoterService
from services.admin_service import AdminService
from services.report_service import ReportService
from utils.validators import REQUIRED_EDUCATION_LEVELS, MIN_CANDIDATE_AGE, MAX_CANDIDATE_AGE

class AdminUI:
    def __init__(self, state: AppState, current_user: dict):
        self.state = state
        self.user = current_user
        self.cand_svc = CandidateService(state)
        self.stn_svc = StationService(state)
        self.pos_svc = PositionService(state)
        self.poll_svc = PollService(state)
        self.voter_svc = VoterService(state)
        self.admin_svc = AdminService(state)
        self.rpt_svc = ReportService(state)

    def run_dashboard(self):
        dispatch = {
            "1": self.ui_create_candidate, "2": self.ui_view_candidates, "3": self.ui_update_candidate, "4": self.ui_delete_candidate, "5": self.ui_search_candidates,
            "6": self.ui_create_station, "7": self.ui_view_stations, "8": self.ui_update_station, "9": self.ui_delete_station,
            "10": self.ui_create_position, "11": self.ui_view_positions, "12": self.ui_update_position, "13": self.ui_delete_position,
            "14": self.ui_create_poll, "15": self.ui_view_polls, "16": self.ui_update_poll, "17": self.ui_delete_poll, "18": self.ui_open_close_poll, "19": self.ui_assign_candidates,
            "20": self.ui_view_voters, "21": self.ui_verify_voter, "22": self.ui_deactivate_voter, "23": self.ui_search_voters,
            "24": self.ui_create_admin, "25": self.ui_view_admins, "26": self.ui_deactivate_admin,
            "27": self.ui_view_poll_results, "28": self.ui_view_detailed_statistics, "29": self.ui_view_audit_log, "30": self.ui_station_wise_results,
            "31": self.ui_save_data
        }

        while True:
            clear_screen()
            header("ADMIN DASHBOARD", THEME_ADMIN)
            print(f"  {THEME_ADMIN}  ● {RESET}{BOLD}{self.user['full_name']}{RESET}  {DIM}│  Role: {self.user['role']}{RESET}")

            subheader("Candidate Management", THEME_ADMIN_ACCENT)
            menu_item(1, "Create Candidate", THEME_ADMIN); menu_item(2, "View All Candidates", THEME_ADMIN)
            menu_item(3, "Update Candidate", THEME_ADMIN); menu_item(4, "Delete Candidate", THEME_ADMIN); menu_item(5, "Search Candidates", THEME_ADMIN)

            subheader("Voting Station Management", THEME_ADMIN_ACCENT)
            menu_item(6, "Create Voting Station", THEME_ADMIN); menu_item(7, "View All Stations", THEME_ADMIN)
            menu_item(8, "Update Station", THEME_ADMIN); menu_item(9, "Delete Station", THEME_ADMIN)

            subheader("Polls & Positions", THEME_ADMIN_ACCENT)
            menu_item(10, "Create Position", THEME_ADMIN); menu_item(11, "View Positions", THEME_ADMIN)
            menu_item(12, "Update Position", THEME_ADMIN); menu_item(13, "Delete Position", THEME_ADMIN)
            menu_item(14, "Create Poll", THEME_ADMIN); menu_item(15, "View All Polls", THEME_ADMIN)
            menu_item(16, "Update Poll", THEME_ADMIN); menu_item(17, "Delete Poll", THEME_ADMIN)
            menu_item(18, "Open/Close Poll", THEME_ADMIN); menu_item(19, "Assign Candidates to Poll", THEME_ADMIN)

            subheader("Voter Management", THEME_ADMIN_ACCENT)
            menu_item(20, "View All Voters", THEME_ADMIN); menu_item(21, "Verify Voter", THEME_ADMIN)
            menu_item(22, "Deactivate Voter", THEME_ADMIN); menu_item(23, "Search Voters", THEME_ADMIN)

            subheader("Admin Management", THEME_ADMIN_ACCENT)
            menu_item(24, "Create Admin Account", THEME_ADMIN); menu_item(25, "View Admins", THEME_ADMIN); menu_item(26, "Deactivate Admin", THEME_ADMIN)

            subheader("Results & Reports", THEME_ADMIN_ACCENT)
            menu_item(27, "View Poll Results", THEME_ADMIN); menu_item(28, "View Detailed Statistics", THEME_ADMIN)
            menu_item(29, "View Audit Log", THEME_ADMIN); menu_item(30, "Station-wise Results", THEME_ADMIN)

            subheader("System", THEME_ADMIN_ACCENT)
            menu_item(31, "Save Data", THEME_ADMIN); menu_item(32, "Logout", THEME_ADMIN)
            
            print()
            choice = prompt("Enter choice: ")

            if choice == "32":
                self.state.save()
                break
            elif choice in dispatch:
                dispatch[choice]()
            else:
                error("Invalid choice."); pause()

    # ── Candidates ────────────────────────────────────────────

    def ui_create_candidate(self):
        clear_screen(); header("CREATE NEW CANDIDATE", THEME_ADMIN)
        print()
        data = {
            "full_name": prompt("Full Name: "),
            "national_id": prompt("National ID: "),
            "date_of_birth": prompt("Date of Birth (YYYY-MM-DD): "),
            "gender": prompt("Gender (M/F/Other): ").upper(),
        }
        subheader("Education Levels", THEME_ADMIN_ACCENT)
        for i, level in enumerate(REQUIRED_EDUCATION_LEVELS, 1):
            print(f"    {THEME_ADMIN}{i}.{RESET} {level}")
        try:
            edu_choice = int(prompt("Select education level: "))
            data["education"] = REQUIRED_EDUCATION_LEVELS[edu_choice - 1]
        except (ValueError, IndexError):
            data["education"] = ""
        
        data["party"] = prompt("Political Party/Affiliation: ")
        data["manifesto"] = prompt("Brief Manifesto/Bio: ")
        data["address"] = prompt("Address: ")
        data["phone"] = prompt("Phone: ")
        data["email"] = prompt("Email: ")
        data["criminal_record"] = prompt("Has Criminal Record? (yes/no): ").lower()
        data["years_experience"] = prompt("Years of Public Service/Political Experience: ")

        res = self.cand_svc.create(data, self.user["username"])
        if res["ok"]: success(f"Candidate created! ID: {res['id']}")
        else: error(res["error"])
        pause()

    def ui_view_candidates(self):
         clear_screen(); header("ALL CANDIDATES", THEME_ADMIN)
         cands = self.state.candidates
         if not cands: print(); info("No candidates found."); pause(); return
         print()
         table_header(f"{'ID':<5} {'Name':<25} {'Party':<20} {'Age':<5} {'Education':<20} {'Status':<10}", THEME_ADMIN)
         table_divider(85, THEME_ADMIN)
         for cid, c in cands.items():
             status = status_badge("Active", True) if c["is_active"] else status_badge("Inactive", False)
             print(f"  {c['id']:<5} {c['full_name']:<25} {c['party']:<20} {c['age']:<5} {c['education']:<20} {status}")
         print(f"\n  {DIM}Total Candidates: {len(cands)}{RESET}"); pause()

    def ui_update_candidate(self):
        clear_screen(); header("UPDATE CANDIDATE", THEME_ADMIN)
        try: cid = int(prompt("Enter Candidate ID: "))
        except ValueError: error("Invalid ID."); pause(); return
        if cid not in self.state.candidates: error("Not found."); pause(); return
        c = self.state.candidates[cid]
        info("Press Enter to keep current value\n")
        data = {
            "full_name": prompt(f"Full Name [{c['full_name']}]: "),
            "party": prompt(f"Party [{c['party']}]: "),
            "manifesto": prompt(f"Manifesto [{c.get('manifesto','')}]: "),
            "phone": prompt(f"Phone [{c.get('phone','')}]: "),
            "email": prompt(f"Email [{c.get('email','')}]: "),
            "address": prompt(f"Address [{c.get('address','')}]: "),
            "years_experience": prompt(f"Years Experience [{c.get('years_experience','')}]: ")
        }
        res = self.cand_svc.update(cid, data, self.user["username"])
        if res["ok"]: success("Candidate updated.")
        else: error(res["error"])
        pause()

    def ui_delete_candidate(self):
        clear_screen(); header("DELETE CANDIDATE", THEME_ADMIN)
        try: cid = int(prompt("Enter Candidate ID to deactivate: "))
        except ValueError: error("Invalid ID."); pause(); return
        if prompt("Are you sure? (yes/no): ").lower() == "yes":
            res = self.cand_svc.deactivate(cid, self.user["username"])
            if res["ok"]: success(f"Deactivated candidate {res['name']}")
            else: error(res["error"])
        pause()

    def ui_search_candidates(self):
        clear_screen(); header("SEARCH CANDIDATES", THEME_ADMIN)
        menu_item(1, "Name", THEME_ADMIN); menu_item(2, "Party", THEME_ADMIN); menu_item(3, "Education", THEME_ADMIN); menu_item(4, "Age Range", THEME_ADMIN)
        choice = prompt("Choice: ")
        results = []
        if choice == "1": results = self.cand_svc.search("name", prompt("Name: "))
        elif choice == "2": results = self.cand_svc.search("party", prompt("Party: "))
        elif choice == "3": 
            for i, level in enumerate(REQUIRED_EDUCATION_LEVELS, 1): print(f"    {THEME_ADMIN}{i}.{RESET} {level}")
            try: results = self.cand_svc.search("education", REQUIRED_EDUCATION_LEVELS[int(prompt("Select: ")) - 1])
            except: pass
        elif choice == "4":
            try: results = self.cand_svc.search("age_range", (int(prompt("Min age: ")), int(prompt("Max age: "))))
            except: pass
        
        if not results: info("None found.")
        else:
            for c in results: print(f"  ID:{c['id']} | {c['full_name']} | {c['party']}")
        pause()

    # ── Stations ──────────────────────────────────────────────

    def ui_create_station(self):
        clear_screen(); header("CREATE STATION", THEME_ADMIN)
        data = {
            "name": prompt("Station Name: "), "location": prompt("Location/Address: "),
            "region": prompt("Region/District: "), "capacity": prompt("Voter Capacity: "),
            "supervisor": prompt("Supervisor: "), "contact": prompt("Contact: "),
            "opening_time": prompt("Opening Time: "), "closing_time": prompt("Closing Time: ")
        }
        res = self.stn_svc.create(data, self.user["username"])
        if res["ok"]: success(f"Station created! ID: {res['id']}")
        else: error(res["error"])
        pause()

    def ui_view_stations(self):
        clear_screen(); header("ALL STATIONS", THEME_ADMIN)
        if not self.state.voting_stations: info("None found."); pause(); return
        table_header(f"{'ID':<5} {'Name':<25} {'Location':<25} {'Cap.':<8} {'Reg.':<8} {'Status':<10}", THEME_ADMIN)
        table_divider(96, THEME_ADMIN)
        for sid, s in self.state.voting_stations.items():
            rc = self.stn_svc.voter_count(sid)
            st = status_badge("Active", True) if s["is_active"] else status_badge("Inactive", False)
            print(f"  {s['id']:<5} {s['name']:<25} {s['location']:<25} {s['capacity']:<8} {rc:<8} {st}")
        pause()

    def ui_update_station(self):
        clear_screen(); header("UPDATE STATION", THEME_ADMIN)
        try: sid = int(prompt("Station ID: "))
        except ValueError: return
        if sid not in self.state.voting_stations: error("Not found."); pause(); return
        s = self.state.voting_stations[sid]
        data = {
            "name": prompt(f"Name [{s['name']}]: "), "location": prompt(f"Location [{s['location']}]: "),
            "capacity": prompt(f"Capacity [{s['capacity']}]: "), "supervisor": prompt(f"Supervisor [{s.get('supervisor','')}]: ")
        }
        res = self.stn_svc.update(sid, data, self.user["username"])
        if res["ok"]: success("Updated.")
        else: error(res["error"])
        pause()

    def ui_delete_station(self):
        clear_screen(); header("DELETE STATION", THEME_ADMIN)
        try: sid = int(prompt("Station ID: "))
        except ValueError: return
        res = self.stn_svc.deactivate(sid, self.user["username"])
        if not res["ok"] and res.get("needs_confirm"):
            warning(f"{res['voter_count']} voters are registered here.")
            if prompt("Force deactivation? (yes/no): ").lower() == "yes":
                res = self.stn_svc.deactivate(sid, self.user["username"], force=True)
            else: info("Cancelled."); pause(); return
        if res["ok"]: success(f"Deactivated {res['name']}")
        else: error(res.get("error", "Failed"))
        pause()

    # ── Positions ─────────────────────────────────────────────

    def ui_create_position(self):
        clear_screen(); header("CREATE POSITION", THEME_ADMIN)
        data = {
            "title": prompt("Title: "), "description": prompt("Description: "),
            "level": prompt("Level (National/Regional/Local): "),
            "max_winners": prompt("Number of winners/seats: "),
            "min_candidate_age": prompt(f"Minimum candidate age [{MIN_CANDIDATE_AGE}–{MAX_CANDIDATE_AGE}]: ")
        }
        res = self.pos_svc.create(data, self.user["username"])
        if res["ok"]: success(f"Position created! ID: {res['id']}")
        else: error(res["error"])
        pause()

    def ui_view_positions(self):
        clear_screen(); header("ALL POSITIONS", THEME_ADMIN)
        if not self.state.positions: info("None."); pause(); return
        table_header(f"{'ID':<5} {'Title':<25} {'Level':<12} {'Seats':<8} {'Min Age':<10}", THEME_ADMIN)
        for pid, p in self.state.positions.items():
            print(f"  {p['id']:<5} {p['title']:<25} {p['level']:<12} {p['max_winners']:<8} {p.get('min_candidate_age', 0):<10}")
        pause()

    def ui_update_position(self):
        clear_screen(); header("UPDATE POSITION", THEME_ADMIN)
        try: pid = int(prompt("Position ID: "))
        except ValueError: return
        if pid not in self.state.positions: error("Not found."); pause(); return
        p = self.state.positions[pid]
        data = {
            "title": prompt(f"Title [{p['title']}]: "), "level": prompt(f"Level [{p['level']}]: "),
            "max_winners": prompt(f"Seats [{p['max_winners']}]: ")
        }
        res = self.pos_svc.update(pid, data, self.user["username"])
        if res["ok"]: success("Updated.")
        else: error(res["error"])
        pause()

    def ui_delete_position(self):
        clear_screen(); header("DELETE POSITION", THEME_ADMIN)
        try: pid = int(prompt("Position ID: "))
        except ValueError: return
        res = self.pos_svc.deactivate(pid, self.user["username"])
        if res["ok"]: success("Deactivated.")
        else: error(res["error"])
        pause()

    # ── Polls ─────────────────────────────────────────────────

    def ui_create_poll(self):
        clear_screen(); header("CREATE POLL", THEME_ADMIN)
        data = {
            "title": prompt("Title: "),
            "description": prompt("Description: "),
            "election_type": prompt("Election Type (General/Primary/By-election/Referendum): "),
            "start_date": prompt("Start Date (YYYY-MM-DD): "),
            "end_date": prompt("End Date (YYYY-MM-DD): ")
        }
        try:
            data["position_ids"] = [int(x.strip()) for x in prompt("Enter Position IDs (comma-separated): ").split(",") if x.strip()]
            data["station_ids"] = [int(x.strip()) for x in prompt("Enter Station IDs (comma-separated): ").split(",") if x.strip()]
        except ValueError: error("Invalid IDs."); pause(); return
        
        res = self.poll_svc.create(data, self.user["username"])
        if res["ok"]: success(f"Poll created! ID: {res['id']}")
        else: error(res["error"])
        pause()

    def ui_view_polls(self):
        clear_screen(); header("ALL POLLS", THEME_ADMIN)
        for pid, p in self.state.polls.items():
            sc = "\033[32m" if p['status'] == 'open' else ("\033[33m" if p['status'] == 'draft' else "\033[31m")
            print(f"\n  {BOLD}{THEME_ADMIN}Poll #{p['id']}: {p['title']}{RESET}  {DIM}Status:{RESET} {sc}{BOLD}{p['status'].upper()}{RESET}")
            for pos in p["positions"]:
                cnames = [self.state.candidates[cid]["full_name"] for cid in pos["candidate_ids"] if cid in self.state.candidates]
                print(f"    {THEME_ADMIN_ACCENT}▸{RESET} {pos['position_title']}: {', '.join(cnames) if cnames else 'None'}")
        pause()

    def ui_update_poll(self): pass
    def ui_delete_poll(self): pass

    def ui_open_close_poll(self):
        clear_screen(); header("OPEN/CLOSE POLL", THEME_ADMIN)
        try: pid = int(prompt("Poll ID: "))
        except ValueError: return
        if pid not in self.state.polls: error("Not found."); pause(); return
        p = self.state.polls[pid]
        print(f"Current status: {p['status']}")
        cmd = "open" if p["status"] in ("draft", "closed") else "closed"
        if prompt(f"Change to {cmd}? (yes/no): ").lower() == "yes":
            res = self.poll_svc.set_status(pid, cmd, self.user["username"])
            if res["ok"]: success(f"Poll is now {cmd}.")
            else: error(res["error"])
        pause()

    def ui_assign_candidates(self):
        clear_screen(); header("ASSIGN CANDIDATES", THEME_ADMIN)
        try: pid = int(prompt("Poll ID: "))
        except ValueError: return
        if pid not in self.state.polls: return
        poll = self.state.polls[pid]
        assignments = {}
        for idx, pos in enumerate(poll["positions"]):
            print(f"\n  {THEME_ADMIN_ACCENT}▸ Position: {pos['position_title']}{RESET}")
            try:
                cids = [int(x.strip()) for x in prompt("Candidate IDs (comma-separated): ").split(",") if x.strip()]
                assignments[idx] = cids
            except ValueError: pass
        if assignments:
            res = self.poll_svc.assign_candidates(pid, assignments, self.user["username"])
            if res["ok"]: success("Assigned.")
            else: error(res["error"])
        pause()

    # ── Voters / Admins / Reports / Save wrappers ─────────────
    
    def ui_view_voters(self):
        clear_screen(); header("ALL VOTERS", THEME_ADMIN)
        for v in self.state.voters.values():
            st = status_badge("Verified", True) if v['is_verified'] else status_badge("Unverified", False)
            print(f"  {v['id']:<5} {v['full_name']:<25} {v['voter_card_number']:<15} {st}")
        pause()

    def ui_verify_voter(self):
        try: vid = int(prompt("Voter ID to verify: "))
        except ValueError: return
        res = self.voter_svc.verify(vid, self.user["username"])
        if res["ok"]: success("Verified.")
        else: error(res["error"])
        pause()

    def ui_deactivate_voter(self): pass
    def ui_search_voters(self): pass
    def ui_create_admin(self): pass
    def ui_view_admins(self): pass
    def ui_deactivate_admin(self): pass

    def ui_view_poll_results(self):
        clear_screen(); header("POLL RESULTS", THEME_ADMIN)
        try: pid = int(prompt("Poll ID: "))
        except ValueError: return
        res = self.rpt_svc.poll_results(pid)
        if not res: error("Not found."); pause(); return
        print(f"\n  Turnout: {res['turnout']:.1f}%")
        for pos in res["positions"]:
            print(f"\n  {THEME_ADMIN_ACCENT}{pos['position_title']}{RESET}")
            for cid, count in sorted(pos["vote_counts"].items(), key=lambda x: x[1], reverse=True):
                name = pos["candidates"].get(cid, {}).get("full_name", "?")
                print(f"    {name}: {count} votes")
        pause()

    def ui_view_detailed_statistics(self):
        clear_screen(); header("SYSTEM STATS", THEME_ADMIN)
        stat = self.rpt_svc.system_statistics()
        print(f"  Candidates: {stat['candidates']['active']} active")
        print(f"  Voters: {stat['voters']['active']} active")
        print(f"  Stations: {stat['stations']['active']} active")
        print(f"  Total Votes Cast in System: {stat['total_votes']}")
        pause()

    def ui_station_wise_results(self): pass
    
    def ui_view_audit_log(self):
        clear_screen(); header("AUDIT LOG", THEME_ADMIN)
        logs = self.rpt_svc.audit_entries()
        for l in logs:
            print(f"  {DIM}{l['timestamp'][:19]}{RESET} {l['action']:<25} {l['user']:<20} {l['details']}")
        pause()

    def ui_save_data(self):
        self.state.save()
        success("Saved."); pause()
