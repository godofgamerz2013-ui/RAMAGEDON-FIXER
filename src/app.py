"""ApexRig-AI — dark monochrome Windows performance dashboard."""
import os, sys, time, threading, tkinter as tk
from tkinter import ttk, messagebox, simpledialog
try:
    import keyring
except Exception:
    keyring = None

from engine import scan_processes, ask_gemini, close_pid, hardware_snapshot, log

BG = "#090a0d"
PANEL = "#111318"
PANEL2 = "#171a21"
LINE = "#282d37"
TEXT = "#f2f3f5"
MUTED = "#9299a6"
ACCENT = "#d8dce3"
WARN = "#e0b66f"
RED = "#e07878"

class ApexApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ApexRig-AI")
        self.geometry("1280x820")
        self.minsize(1080, 700)
        self.configure(bg=BG)
        self.key = (keyring.get_password("ApexRig-AI", "gemini") if keyring else None) or ""
        self.monitoring = False
        self.last_scan = 0
        self.last_ai = 0
        self.rows = []
        self.page = None
        self.pages = {}
        self._style()
        self._shell()
        self.show_page("Overview")
        self.refresh()
        self.after(1000, self.tick)

    def _style(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("Treeview", background=PANEL, foreground=TEXT, fieldbackground=PANEL,
                    borderwidth=0, rowheight=34, font=("Segoe UI", 10))
        s.configure("Treeview.Heading", background=PANEL2, foreground=ACCENT,
                    relief="flat", font=("Segoe UI Semibold", 9))
        s.map("Treeview", background=[("selected", "#343a46")], foreground=[("selected", "#ffffff")])
        s.configure("TNotebook", background=BG, borderwidth=0)
        s.configure("TProgressbar", troughcolor=PANEL2, background="#c4cad4", bordercolor=PANEL2)

    def _shell(self):
        self.sidebar = tk.Frame(self, bg=PANEL, width=224)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        brand = tk.Frame(self.sidebar, bg=PANEL)
        brand.pack(fill="x", padx=22, pady=(26, 30))
        tk.Label(brand, text="APEXRIG", bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 21, "bold")).pack(anchor="w")
        tk.Label(brand, text="AI  /  SYSTEM CONTROL", bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(3, 0))
        tk.Frame(self.sidebar, bg=LINE, height=1).pack(fill="x", padx=16, pady=(0, 16))
        self.nav = {}
        for name, glyph in [("Overview", "◫"), ("Processes", "▤"), ("Gemini AI", "✧"),
                            ("Hardware", "⌁"), ("Settings", "⚙")]:
            b = tk.Button(self.sidebar, text=f"   {glyph}     {name}", anchor="w",
                          command=lambda n=name: self.show_page(n), relief="flat",
                          bd=0, bg=PANEL, fg=MUTED, activebackground=PANEL2,
                          activeforeground=TEXT, font=("Segoe UI", 10), padx=12, pady=13)
            b.pack(fill="x", padx=12, pady=2)
            self.nav[name] = b
        tk.Frame(self.sidebar, bg=LINE, height=1).pack(fill="x", padx=16, pady=(22, 12))
        tk.Label(self.sidebar, text="LIVE SESSION", bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=24)
        self.side_status = tk.Label(self.sidebar, text="●  MONITORING PAUSED",
                                    bg=PANEL, fg=WARN, font=("Segoe UI", 8, "bold"))
        self.side_status.pack(anchor="w", padx=24, pady=(8, 0))
        tk.Label(self.sidebar, text="TEMP-RUN EDITION", bg=PANEL, fg="#626a77",
                 font=("Segoe UI", 8)).pack(side="bottom", anchor="w", padx=24, pady=22)

        self.main = tk.Frame(self, bg=BG)
        self.main.pack(side="left", fill="both", expand=True)
        top = tk.Frame(self.main, bg=BG, height=76)
        top.pack(fill="x", padx=30, pady=(18, 4))
        top.pack_propagate(False)
        self.page_title = tk.Label(top, text="Overview", bg=BG, fg=TEXT,
                                   font=("Segoe UI", 21, "bold"))
        self.page_title.pack(side="left", anchor="center")
        self.top_status = tk.Label(top, text="● PAUSED", bg=BG, fg=WARN,
                                   font=("Segoe UI", 9, "bold"))
        self.top_status.pack(side="right", anchor="center")
        tk.Frame(self.main, bg=LINE, height=1).pack(fill="x", padx=30)
        self.content = tk.Frame(self.main, bg=BG)
        self.content.pack(fill="both", expand=True, padx=30, pady=22)

    def card(self, parent, title, value="—", hint=""):
        box = tk.Frame(parent, bg=PANEL, highlightbackground=LINE, highlightthickness=1)
        tk.Label(box, text=title.upper(), bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=17, pady=(15, 5))
        val = tk.Label(box, text=value, bg=PANEL, fg=TEXT,
                       font=("Segoe UI", 23, "bold"))
        val.pack(anchor="w", padx=17)
        tk.Label(box, text=hint, bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 8)).pack(anchor="w", padx=17, pady=(3, 15))
        return box, val

    def action(self, parent, text, command, primary=False):
        return tk.Button(parent, text=text, command=command, relief="flat", bd=0,
                         bg="#d7dbe2" if primary else PANEL2,
                         fg="#111318" if primary else TEXT,
                         activebackground="#ffffff" if primary else "#252a33",
                         activeforeground="#111318" if primary else TEXT,
                         font=("Segoe UI", 9, "bold"), padx=16, pady=10, cursor="hand2")

    def show_page(self, name):
        for w in self.content.winfo_children():
            w.destroy()
        for n, b in self.nav.items():
            b.configure(bg=PANEL2 if n == name else PANEL,
                        fg=TEXT if n == name else MUTED)
        self.page_title.configure(text=name)
        self.page = name
        getattr(self, "build_" + name.lower().replace(" ", "_"))()

    def build_overview(self):
        tk.Label(self.content, text="Performance at a glance",
                 bg=BG, fg=TEXT, font=("Segoe UI", 16, "bold")).pack(anchor="w")
        tk.Label(self.content, text="A clean view of system load, memory pressure and background activity.",
                 bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", pady=(4, 18))
        cards = tk.Frame(self.content, bg=BG)
        cards.pack(fill="x")
        self.ram_card, self.ram_value = self.card(cards, "Memory usage", "—", "Used / total RAM")
        self.cpu_card, self.cpu_value = self.card(cards, "CPU load", "—", "Current utilization")
        self.proc_card, self.proc_value = self.card(cards, "Processes", "—", "Large memory consumers")
        for c in (self.ram_card, self.cpu_card, self.proc_card):
            c.pack(side="left", fill="x", expand=True, padx=(0, 12))
        row = tk.Frame(self.content, bg=BG)
        row.pack(fill="x", pady=20)
        self.action(row, "START MONITORING", self.toggle_monitoring, True).pack(side="left")
        self.action(row, "SCAN NOW", self.refresh).pack(side="left", padx=8)
        self.action(row, "OPEN GEMINI", lambda: self.show_page("Gemini AI")).pack(side="left")
        lower = tk.Frame(self.content, bg=BG)
        lower.pack(fill="both", expand=True)
        left = tk.Frame(lower, bg=PANEL, highlightbackground=LINE, highlightthickness=1)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        tk.Label(left, text="RECENT ACTIVITY", bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=16, pady=14)
        self.activity = tk.Text(left, bg=PANEL, fg="#c7ccd5", insertbackground=TEXT,
                                relief="flat", height=10, font=("Consolas", 9), state="disabled")
        self.activity.pack(fill="both", expand=True, padx=14, pady=(0, 12))
        right = tk.Frame(lower, bg=PANEL, width=250, highlightbackground=LINE, highlightthickness=1)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        tk.Label(right, text="SAFETY STATUS", bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=16, pady=14)
        for line in ["System processes protected", "AI recommendations are advisory",
                     "Manual confirmation required", "Hardware tuning is read-only"]:
            tk.Label(right, text="✓  " + line, bg=PANEL, fg=TEXT,
                     font=("Segoe UI", 9), wraplength=210, justify="left").pack(anchor="w", padx=16, pady=7)

    def build_processes(self):
        tk.Label(self.content, text="Memory consumers", bg=BG, fg=TEXT,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")
        tk.Label(self.content, text="Inspect processes by memory usage. Closing a process always requires confirmation.",
                 bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", pady=(4, 16))
        wrap = tk.Frame(self.content, bg=PANEL, highlightbackground=LINE, highlightthickness=1)
        wrap.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(wrap, columns=("pid", "name", "ram", "cpu", "status"), show="headings")
        for col, label, width in [("pid","PID",80),("name","PROCESS",340),("ram","RAM MB",130),
                                  ("cpu","CPU %",110),("status","STATUS",150)]:
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="w")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        bar = tk.Frame(self.content, bg=BG)
        bar.pack(fill="x", pady=(12, 0))
        self.action(bar, "REFRESH", self.refresh).pack(side="left")
        self.action(bar, "CLOSE SELECTED", self.close_selected, True).pack(side="left", padx=8)

    def build_gemini_ai(self):
        tk.Label(self.content, text="AI-assisted recommendations", bg=BG, fg=TEXT,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")
        tk.Label(self.content, text="Gemini analyses process metadata. It cannot terminate anything automatically; you review and confirm every action.",
                 bg=BG, fg=MUTED, font=("Segoe UI", 9), wraplength=850).pack(anchor="w", pady=(4, 16))
        bar = tk.Frame(self.content, bg=BG)
        bar.pack(fill="x", pady=(0, 12))
        self.action(bar, "ANALYSE PROCESSES", self.analyse, True).pack(side="left")
        self.action(bar, "SET GEMINI API KEY", self.set_key).pack(side="left", padx=8)
        self.recs = tk.Text(self.content, bg=PANEL, fg=TEXT, insertbackground=TEXT,
                            relief="flat", font=("Consolas", 10), padx=16, pady=14)
        self.recs.pack(fill="both", expand=True)
        self.recs.insert("end", "No analysis yet. Add your Gemini API key, then run an analysis.")

    def build_hardware(self):
        tk.Label(self.content, text="Hardware telemetry", bg=BG, fg=TEXT,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")
        tk.Label(self.content, text="Live read-only sensor information. No clock, voltage, BIOS or power-limit changes.",
                 bg=BG, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", pady=(4, 16))
        self.hwtext = tk.Label(self.content, text="Loading…", bg=PANEL, fg=TEXT,
                               font=("Consolas", 12), justify="left", anchor="nw",
                               padx=22, pady=22)
        self.hwtext.pack(fill="x")
        self.action(self.content, "REFRESH TELEMETRY", self.refresh).pack(anchor="w", pady=14)

    def build_settings(self):
        tk.Label(self.content, text="Application settings", bg=BG, fg=TEXT,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")
        tk.Label(self.content, text="Startup checks for the latest public GitHub version and runs from Windows TEMP.",
                 bg=BG, fg=MUTED, font=("Segoe UI", 9), wraplength=850).pack(anchor="w", pady=(4, 18))
        panel = tk.Frame(self.content, bg=PANEL, highlightbackground=LINE, highlightthickness=1)
        panel.pack(fill="x")
        tk.Label(panel, text="Launch ApexRig-AI when I sign in", bg=PANEL, fg=TEXT,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=18, pady=(18, 5))
        tk.Label(panel, text="Registers a per-user Windows startup command. It stores only the launcher command, not the app files. Each sign-in downloads the latest main branch into TEMP.",
                 bg=PANEL, fg=MUTED, font=("Segoe UI", 9), wraplength=800, justify="left").pack(anchor="w", padx=18)
        self.startup_var = tk.BooleanVar(value=self.startup_enabled())
        tk.Checkbutton(panel, text="Enable automatic startup and update", variable=self.startup_var,
                       command=self.set_startup, bg=PANEL, fg=TEXT, selectcolor=PANEL2,
                       activebackground=PANEL, activeforeground=TEXT,
                       font=("Segoe UI", 10)).pack(anchor="w", padx=14, pady=14)
        tk.Label(self.content, text="TEMP lifecycle", bg=BG, fg=TEXT,
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(24, 8))
        tk.Label(self.content, text="The app runs from a temporary extracted copy. Files are removed when it exits normally. If Windows loses power or is forced off, the next boot removes stale ApexRig temporary folders. Logs and Gemini credentials are stored separately in your user profile / Windows Credential Manager.",
                 bg=BG, fg=MUTED, wraplength=880, justify="left",
                 font=("Segoe UI", 9)).pack(anchor="w")

    @staticmethod
    def widget_alive(widget):
        """Return False for widgets destroyed during page navigation."""
        if widget is None:
            return False
        try:
            return bool(widget.winfo_exists())
        except (tk.TclError, RuntimeError):
            return False

    def say(self, msg):
        line = log(msg)
        activity = getattr(self, "activity", None)
        if self.widget_alive(activity):
            try:
                activity.configure(state="normal")
                activity.insert("end", line + "\n")
                activity.see("end")
                activity.configure(state="disabled")
            except tk.TclError:
                pass

    def set_key(self):
        value = simpledialog.askstring("Gemini API key", "Paste your Gemini API key:", show="*")
        if value:
            if not keyring:
                messagebox.showerror("Secure storage unavailable", "Install keyring to use Windows Credential Manager.")
                return
            keyring.set_password("ApexRig-AI", "gemini", value)
            self.key = value
            self.say("Gemini key saved in Windows Credential Manager.")

    def toggle_monitoring(self):
        self.monitoring = not self.monitoring
        state = "ACTIVE" if self.monitoring else "PAUSED"
        color = ACCENT if self.monitoring else WARN
        self.top_status.configure(text="● " + state, fg=color)
        self.side_status.configure(text="●  MONITORING " + state, fg=color)
        self.say("Monitoring " + state.lower())
        if self.monitoring:
            self.last_scan = time.time()

    def refresh(self):
        try:
            h = hardware_snapshot()
            self.rows = scan_processes()
            # Widget attributes survive page changes, but their Tk widgets do not.
            if self.page == "Overview":
                if self.widget_alive(getattr(self, "ram_value", None)):
                    self.ram_value.configure(text=f"{h['ram_percent']}%")
                if self.widget_alive(getattr(self, "cpu_value", None)):
                    self.cpu_value.configure(text=f"{h['cpu_percent']}%")
                if self.widget_alive(getattr(self, "proc_value", None)):
                    self.proc_value.configure(text=str(len(self.rows)))
            if self.page == "Processes" and self.widget_alive(getattr(self, "tree", None)):
                for item in self.tree.get_children():
                    self.tree.delete(item)
                for p in self.rows:
                    self.tree.insert("", "end", values=(p["pid"], p["name"], p["ram_mb"], p["cpu_pct"], p["status"]))
            if self.page == "Hardware" and self.widget_alive(getattr(self, "hwtext", None)):
                self.hwtext.configure(text=(
                    f"CPU utilization : {h['cpu_percent']}%\nCPU clock        : {h['cpu_mhz'] or 'N/A'} MHz\n"
                    f"Memory           : {h['ram_used_gb']} / {h['ram_total_gb']} GB ({h['ram_percent']}%)\n"
                    f"GPU              : {h['gpu']}\n\nREAD-ONLY TELEMETRY"
                ))
            self.last_scan = time.time()
            self.say("System scan completed.")
        except Exception as exc:
            self.say("Scan error: " + str(exc))

    def close_selected(self):
        selected = self.tree.selection()
        if not selected:
            return
        pid, name, *_ = self.tree.item(selected[0], "values")
        if messagebox.askyesno("Confirm process close", f"Close {name} (PID {pid})? Save any open work first."):
            ok, result = close_pid(int(pid), name)
            self.say(result)
            messagebox.showinfo("ApexRig-AI", result)
            self.refresh()

    def analyse(self):
        if not self.key:
            self.set_key()
        if not self.key:
            return
        self.last_ai = time.time()
        if not self.widget_alive(getattr(self, "recs", None)):
            return
        self.recs.delete("1.0", "end")
        self.recs.insert("end", "Gemini is analysing the current process snapshot…")
        def worker():
            try:
                snapshot = scan_processes()
                result = ask_gemini(snapshot, self.key)
                self.after(0, lambda: self.show_results(snapshot, result))
            except Exception as exc:
                error_text = str(exc)  # Exception variables are cleared after the except block.
                try:
                    self.after(0, lambda msg=error_text: self.show_analysis_error(msg))
                except tk.TclError:
                    pass
        threading.Thread(target=worker, daemon=True).start()

    def show_analysis_error(self, error_text):
        if self.page != "Gemini AI" or not self.widget_alive(getattr(self, "recs", None)):
            return
        self.recs.insert("end", "\n\nAnalysis failed: " + error_text)

    def show_results(self, snapshot, result):
        if self.page != "Gemini AI" or not self.widget_alive(getattr(self, "recs", None)):
            return
        names = {p["pid"]: p["name"] for p in snapshot}
        self.recs.delete("1.0", "end")
        if not result:
            self.recs.insert("end", "No recommendations returned. No processes were changed.")
        for item in result:
            self.recs.insert("end", f"PID {item['pid']}  |  {names.get(item['pid'], 'Unknown')}\n{item.get('reason', 'No reason supplied.')}\n\n")
        self.recs.insert("end", "\nNothing was closed. Use the Processes tab and confirm any close manually.")
        self.say(f"Gemini returned {len(result)} recommendation(s); no processes were terminated.")

    def startup_enabled(self):
        if os.name != "nt":
            return False
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run") as k:
                winreg.QueryValueEx(k, "ApexRigAI")
            return True
        except Exception:
            return False

    def set_startup(self):
        if os.name != "nt":
            messagebox.showerror("Windows only", "Startup integration is available on Windows.")
            return
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        command = "powershell.exe -NoProfile -WindowStyle Hidden -Command \"Invoke-RestMethod -Uri 'https://raw.githubusercontent.com/godofgamerz2013-ui/RAMAGEDON-FIXER/main/ONE-CLICK-BOOT.ps1' | Invoke-Expression\""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as k:
                if self.startup_var.get():
                    winreg.SetValueEx(k, "ApexRigAI", 0, winreg.REG_SZ, command)
                    self.say("Automatic startup enabled.")
                else:
                    try:
                        winreg.DeleteValue(k, "ApexRigAI")
                    except FileNotFoundError:
                        pass
                    self.say("Automatic startup disabled.")
        except Exception as exc:
            self.startup_var.set(not self.startup_var.get())
            messagebox.showerror("Startup setting failed", str(exc))

    def tick(self):
        if self.monitoring and time.time() - self.last_scan >= 1200:
            self.refresh()
        self.after(1000, self.tick)

if __name__ == "__main__":
    app = ApexApp()
    app.mainloop()
