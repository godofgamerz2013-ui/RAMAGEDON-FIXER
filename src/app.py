"""ApexRig-AI — minimal Gemini process advisor."""
import tkinter as tk
from tkinter import messagebox
import threading

try:
    import keyring
except Exception:
    keyring = None

from engine import scan_processes, ask_gemini, log

BG = "#090a0d"
PANEL = "#111318"
LINE = "#282d37"
TEXT = "#f2f3f5"
MUTED = "#9299a6"
ACCENT = "#d8dce3"


class ApexApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ApexRig-AI")
        self.geometry("760x620")
        self.minsize(560, 480)
        self.configure(bg=BG)
        self.key = (keyring.get_password("ApexRig-AI", "gemini") if keyring else None) or ""
        self.busy = False
        self._build()
        if self.key:
            self.key_var.set(self.key)
            self.after(250, self.start_analysis)

    def _build(self):
        shell = tk.Frame(self, bg=BG)
        shell.pack(fill="both", expand=True, padx=42, pady=36)

        tk.Label(shell, text="APEXRIG", bg=BG, fg=TEXT,
                 font=("Segoe UI", 26, "bold")).pack(anchor="w")
        tk.Label(shell, text="GEMINI PC ADVISOR", bg=BG, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(2, 30))

        tk.Label(shell, text="Gemini API key", bg=BG, fg=TEXT,
                 font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.key_var = tk.StringVar()
        self.key_entry = tk.Entry(
            shell, textvariable=self.key_var, show="•",
            bg=PANEL, fg=TEXT, insertbackground=TEXT,
            relief="flat", highlightthickness=1,
            highlightbackground=LINE, highlightcolor=ACCENT,
            font=("Segoe UI", 12)
        )
        self.key_entry.pack(fill="x", ipady=14, pady=(10, 8))
        self.key_entry.bind("<Return>", self._enter)
        tk.Label(shell, text="Paste your key and press ENTER. That's it.",
                 bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w")

        self.status = tk.Label(shell, text="READY", bg=BG, fg=MUTED,
                               font=("Segoe UI", 9, "bold"))
        self.status.pack(anchor="w", pady=(28, 10))

        tk.Frame(shell, bg=LINE, height=1).pack(fill="x", pady=(0, 16))
        tk.Label(shell, text="RESULTS", bg=BG, fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0, 8))
        self.output = tk.Text(
            shell, bg=PANEL, fg=TEXT, insertbackground=TEXT,
            relief="flat", font=("Consolas", 10),
            padx=16, pady=14, wrap="word", state="disabled"
        )
        self.output.pack(fill="both", expand=True)
        self._write("Enter your Gemini API key to analyse your PC.\n\n"
                    "ApexRig only gives recommendations. It will never close processes automatically.")

        if self.key:
            self.key_entry.configure(state="readonly")
        else:
            self.key_entry.focus_set()

    def _enter(self, _event=None):
        self.start_analysis()
        return "break"

    def _write(self, message):
        try:
            self.output.configure(state="normal")
            self.output.delete("1.0", "end")
            self.output.insert("end", message)
            self.output.configure(state="disabled")
        except tk.TclError:
            pass

    def start_analysis(self):
        if self.busy:
            return
        api_key = self.key_var.get().strip()
        if not api_key:
            self.status.configure(text="API KEY REQUIRED", fg="#e07878")
            self.key_entry.focus_set()
            return
        if not keyring:
            self.status.configure(text="SECURE STORAGE UNAVAILABLE", fg="#e07878")
            self._write("Install keyring to securely save your Gemini API key.")
            return
        try:
            keyring.set_password("ApexRig-AI", "gemini", api_key)
        except Exception as exc:
            self.status.configure(text="KEY SAVE FAILED", fg="#e07878")
            self._write("Could not save API key in Windows Credential Manager:\n" + str(exc))
            return

        self.key = api_key
        self.key_entry.configure(state="readonly")
        self.busy = True
        self.status.configure(text="ANALYSING…", fg=ACCENT)
        self._write("Scanning processes and asking Gemini…")
        log("Gemini analysis started.")

        def worker():
            try:
                processes = scan_processes()
                recommendations = ask_gemini(processes, api_key)
                lines = []
                names = {p["pid"]: p["name"] for p in processes}
                if recommendations:
                    for item in recommendations:
                        lines.append(
                            f"{names.get(item['pid'], 'Unknown')}  |  PID {item['pid']}\n"
                            f"{item.get('reason', 'No reason supplied.')}\n"
                        )
                else:
                    lines.append("No process recommendations. Your system looks good.")
                lines.append("\nNo processes were changed.")
                result = "\n".join(lines)
                self.after(0, lambda: self._finish(result, None, len(recommendations)))
            except Exception as exc:
                error = str(exc)
                try:
                    self.after(0, lambda msg=error: self._finish(None, msg, 0))
                except tk.TclError:
                    pass

        threading.Thread(target=worker, daemon=True, name="ApexRig-Gemini").start()

    def _finish(self, result, error, count):
        self.busy = False
        if error:
            self.status.configure(text="ANALYSIS FAILED", fg="#e07878")
            self._write(error)
            log("Gemini analysis failed: " + error)
            # Allow editing the key to correct a bad or restricted API key.
            self.key_entry.configure(state="normal")
            self.key_entry.focus_set()
            return
        self.status.configure(text=f"COMPLETE  •  {count} RECOMMENDATION(S)", fg=ACCENT)
        self._write(result)
        log(f"Gemini returned {count} recommendation(s); no processes were terminated.")


if __name__ == "__main__":
    app = ApexApp()
    app.mainloop()
