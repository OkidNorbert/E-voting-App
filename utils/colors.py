"""
utils/colors.py
ANSI color constants and all terminal display helper functions.
Centralises every print/input helper so the rest of the app never
touches raw ANSI codes directly.
"""
import sys

if sys.platform == "win32":
    import os
    os.system("")

# ── Base styles ────────────────────────────────────────────────
RESET     = "\033[0m"
BOLD      = "\033[1m"
DIM       = "\033[2m"
ITALIC    = "\033[3m"
UNDERLINE = "\033[4m"

# ── Foreground colours ─────────────────────────────────────────
BLACK         = "\033[30m"
RED           = "\033[31m"
GREEN         = "\033[32m"
YELLOW        = "\033[33m"
BLUE          = "\033[34m"
MAGENTA       = "\033[35m"
CYAN          = "\033[36m"
WHITE         = "\033[37m"
GRAY          = "\033[90m"
BRIGHT_RED    = "\033[91m"
BRIGHT_GREEN  = "\033[92m"
BRIGHT_YELLOW = "\033[93m"
BRIGHT_BLUE   = "\033[94m"
BRIGHT_MAGENTA= "\033[95m"
BRIGHT_CYAN   = "\033[96m"
BRIGHT_WHITE  = "\033[97m"

# ── Background colours ─────────────────────────────────────────
BG_RED    = "\033[41m"
BG_GREEN  = "\033[42m"
BG_YELLOW = "\033[43m"
BG_BLUE   = "\033[44m"
BG_MAGENTA= "\033[45m"
BG_CYAN   = "\033[46m"
BG_WHITE  = "\033[47m"
BG_GRAY   = "\033[100m"

# ── Theme aliases ──────────────────────────────────────────────
THEME_LOGIN        = BRIGHT_CYAN
THEME_ADMIN        = BRIGHT_GREEN
THEME_ADMIN_ACCENT = YELLOW
THEME_VOTER        = BRIGHT_BLUE
THEME_VOTER_ACCENT = MAGENTA


# ── Display helpers ────────────────────────────────────────────

def colored(text: str, color: str) -> str:
    return f"{color}{text}{RESET}"

def app_banner() -> None:
    print(f"""{THEME_LOGIN}
  ███████╗    ██╗   ██╗ ██████╗ ████████╗██╗███╗   ██╗ ██████╗ 
  ██╔════╝    ██║   ██║██╔═══██╗╚══██╔══╝██║████╗  ██║██╔════╝ 
  █████╗█████╗██║   ██║██║   ██║   ██║   ██║██╔██╗ ██║██║  ███╗
  ██╔══╝╚════╝╚██╗ ██╔╝██║   ██║   ██║   ██║██║╚██╗██║██║   ██║
  ███████╗     ╚████╔╝ ╚██████╔╝   ██║   ██║██║ ╚████║╚██████╔╝
  ╚══════╝      ╚═══╝   ╚═════╝    ╚═╝   ╚═╝╚═╝  ╚═══╝ ╚═════╝{RESET}
""")

def header(title: str, theme_color: str) -> None:
    width = 58
    print(f"  {theme_color}╭{'─' * width}╮{RESET}")
    print(f"  {theme_color}│{RESET} {BOLD}{theme_color}{title.center(width - 2)}{RESET} {theme_color}│{RESET}")
    print(f"  {theme_color}╰{'─' * width}╯{RESET}")

def panel(text: str, theme_color: str, width: int = 58) -> None:
    lines = text.strip().split("\n")
    print(f"  {theme_color}╭{'─' * width}╮{RESET}")
    for line in lines:
        padded = f" {line} ".ljust(width)
        print(f"  {theme_color}│{RESET}{padded}{theme_color}│{RESET}")
    print(f"  {theme_color}╰{'─' * width}╯{RESET}")

def subheader(title: str, theme_color: str) -> None:
    print(f"\n  {theme_color}{BOLD}► {title}{RESET}")

def table_header(format_str: str, theme_color: str) -> None:
    print(f"  {theme_color}{BOLD}{format_str}{RESET}")

def table_divider(width: int, theme_color: str) -> None:
    print(f"  {theme_color}{'╌' * width}{RESET}")


def error(msg: str) -> None:
    print(f"  {RED}{BOLD} {msg}{RESET}")


def success(msg: str) -> None:
    print(f"  {GREEN}{BOLD} {msg}{RESET}")


def warning(msg: str) -> None:
    print(f"  {YELLOW}{BOLD} {msg}{RESET}")


def info(msg: str) -> None:
    print(f"  {GRAY}{msg}{RESET}")


def menu_item(number: int, text: str, color: str) -> None:
    print(f"  {color}{BOLD}{number:>3}.{RESET}  {text}")


def status_badge(text: str, is_good: bool) -> str:
    return f"{GREEN}{text}{RESET}" if is_good else f"{RED}{text}{RESET}"


def prompt(text: str) -> str:
    return input(f"  {BRIGHT_WHITE}{text}{RESET}").strip()


def masked_input(prompt_text: str = "Password: ") -> str:
    """Cross-platform password input that masks characters with '*'."""
    print(f"  {BRIGHT_WHITE}{prompt_text}{RESET}", end="", flush=True)
    password = ""
    if sys.platform == "win32":
        import msvcrt
        while True:
            ch = msvcrt.getwch()
            if ch in ("\r", "\n"):
                print(); break
            elif ch in ("\x08", "\b"):
                if password:
                    password = password[:-1]
                    sys.stdout.write("\b \b"); sys.stdout.flush()
            elif ch == "\x03":
                raise KeyboardInterrupt
            else:
                password += ch
                sys.stdout.write(f"{YELLOW}*{RESET}"); sys.stdout.flush()
    else:
        import tty, termios
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                ch = sys.stdin.read(1)
                if ch in ("\r", "\n"):
                    print(); break
                elif ch in ("\x7f", "\x08"):
                    if password:
                        password = password[:-1]
                        sys.stdout.write("\b \b"); sys.stdout.flush()
                elif ch == "\x03":
                    raise KeyboardInterrupt
                else:
                    password += ch
                    sys.stdout.write(f"{YELLOW}*{RESET}"); sys.stdout.flush()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return password
