# ApexRig-AI

Windows desktop PC performance companion: Python process/RAM monitoring, Google Gemini recommendations, PID-safe cleanup, and CPU/GPU telemetry.

Safety: Gemini is advisory only. Local code revalidates PIDs. Automatic cleanup is OFF by default; force-kill is OFF by default. Hardware controls are telemetry-only in this release; no voltage/BIOS/clock changes are made.

## Run

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python src\app.py
```

Add your Gemini key inside the app; it is stored with Windows Credential Manager via `keyring`. Default process scan: 20 minutes. Gemini refresh: 40 minutes. Windows 10/11, Python 3.10+.

RAM is used by Windows for caching; indiscriminate clearing can reduce performance. Review AI suggestions before enabling automatic cleanup. Save work before closing apps.
