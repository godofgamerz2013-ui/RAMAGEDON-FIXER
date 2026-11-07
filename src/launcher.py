"""ApexRig-AI startup mode picker. Remembers the user's choice only when requested."""
import json
import os
import subprocess
import sys
import tkinter as tk
from pathlib import Path

PREF_DIR = Path(os.getenv("APPDATA", str(Path.home()))) / "ApexRig-AI"
PREF_FILE = PREF_DIR / "launch.json"
BG, PANEL, LINE = "#090a0d", "#14171d", "#303642"
TEXT, MUTED = "#f2f3f5", "#9299a6"


def load_preference():
    try:
        data = json.loads(PREF_FILE.read_text(encoding="utf-8"))
        mode = data.get("mode")
        return mode if mode in ("gui", "cmd") else None
    except Exception:
        return None


def save_preference(mode):
    PREF_DIR.mkdir(parents=True, exist_ok=True)
    PREF_FILE.write_text(json.dumps({"mode": mode}, indent=2), encoding="utf-8")


def choose_mode():
    remembered = load_preference()
    if remembered:
        return remembered

    root = tk.Tk()
    root.title("ApexRig-AI")
    root.geometry("520x350")
    root.resizable(False, False)
    root.configure(bg=BG)
    choice = {"mode": None}
    remember = tk.BooleanVar(value=False)

    tk.Label(root, text="APEXRIG", bg=BG, fg=TEXT,
             font=("Segoe UI", 25, "bold")).pack(anchor="w", padx=34, pady=(28, 2))
    tk.Label(root, text="HOW DO YOU WANT TO RUN APEXRIG?",
             bg=BG, fg=MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=36, pady=(0, 24))

    def select(mode):
        choice["mode"] = mode
        if remember.get():
            try:
                save_preference(mode)
            except Exception as exc:
                tk.messagebox.showerror("Could not save preference", str(exc))
                return
        root.destroy()

    for mode, title, subtitle in (
        ("gui", "RUN GUI", "Open the desktop interface"),
        ("cmd", "RUN CMD", "Run directly in this terminal"),
    ):
        card = tk.Frame(root, bg=PANEL, highlightbackground=LINE, highlightthickness=1)
        card.pack(fill="x", padx=34, pady=5)
        button = tk.Button(card, text=title, command=lambda m=mode: select(m),
                           bg=PANEL, fg=TEXT, activebackground="#252b35",
                           activeforeground=TEXT, relief="flat", bd=0,
                           font=("Segoe UI", 11, "bold"), anchor="w",
                           padx=16, pady=8)
        button.pack(fill="x")
        tk.Label(card, text=subtitle, bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 9)).pack(anchor="w", padx=17, pady=(0, 10))

    tk.Checkbutton(root, text="Remember my choice and use it on future Windows sign-ins",
                   variable=remember, bg=BG, fg=MUTED, selectcolor=PANEL,
                   activebackground=BG, activeforeground=TEXT,
                   font=("Segoe UI", 9)).pack(anchor="w", padx=34, pady=(15, 0))
    root.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()
    return choice["mode"]


def main():
    mode = choose_mode()
    if not mode:
        return
    base = Path(__file__).resolve().parent
    if mode == "gui":
        python = Path(sys.executable).with_name("pythonw.exe")
        if not python.exists():
            python = Path(sys.executable)
        script = base / "app.py"
        subprocess.run([str(python), str(script)], cwd=str(base), check=False)
    else:
        script = base / "cmd.py"
        subprocess.run([sys.executable, str(script)], cwd=str(base), check=False)


if __name__ == "__main__":
    main()
