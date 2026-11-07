# ApexRig-AI

A Windows performance dashboard with a dark monochrome GUI, process and memory monitoring, optional Gemini advice, and read-only hardware telemetry.

## One-command launch

Open PowerShell and run:

```powershell
irm https://raw.githubusercontent.com/godofgamerz2013-ui/RAMAGEDON-FIXER/main/ONE-CLICK-BOOT.ps1 | iex
```

The bootstrap downloads the latest `main` branch on every launch, extracts it under Windows TEMP, creates a temporary Python environment, installs dependencies, and starts the GUI. It removes the temporary app files when the app exits normally. If Windows is powered off unexpectedly, the next launch attempts to remove stale ApexRig-AI run folders.

**This is TEMP storage, not RAM-only execution.** Windows may retain temporary files after a crash or forced power-off; cleanup is retried on the next launch.

## Automatic startup and updates

In ApexRig-AI, open **Settings → Enable automatic startup and update**. This adds a per-user Windows Run entry containing only a PowerShell command. At each sign-in it fetches the current bootstrap from GitHub, which fetches the latest repository ZIP. Disable the checkbox to remove the startup entry.

Automatic startup requires internet access and Python 3.12 (64-bit) installed and available as `python` on PATH. Startup registration is opt-in.

## Requirements

- Windows 10/11, 64-bit
- Python 3.12 (64-bit)
- Internet access for GitHub downloads and Python packages
- Optional Gemini API key for AI recommendations

## Security and behavior

- Review the bootstrap script before running it: it downloads and executes code from this public repository.
- Gemini recommendations are advisory. The app does not automatically terminate suggested processes; manual close requires confirmation.
- Core Windows, security, driver and audio processes are protected by local checks.
- Hardware telemetry is read-only. No CPU/GPU clock, voltage, BIOS or power-limit changes are performed.
- The GUI and Python environment run from TEMP. Logs and Gemini credentials are stored separately: logs in the user's local application data and API credentials in Windows Credential Manager (when available).
- Startup registration writes one value under the current user's Windows Run key; it does not install a persistent application binary.

## Troubleshooting

- If download fails, check internet access and GitHub availability.
- If Python is not found, install Python 3.12 (64-bit), enable PATH, and reopen PowerShell.
- If pip/package installation is blocked by Windows Application Control, use an administrator-approved route; do not bypass device security policy.
- If some TEMP files remain after a crash, rerun the one-command launcher to trigger stale-folder cleanup.

## Project structure

- `ONE-CLICK-BOOT.ps1` — online bootstrap, update fetch, TEMP extraction and cleanup
- `boot.ps1` — temporary venv/dependency launcher
- `src/app.py` — desktop GUI
- `src/engine.py` — process, Gemini and hardware engine
- `requirements.txt` — Python dependencies

## Build note

The online launcher runs Python source from TEMP. A standalone Windows EXE build is a separate workflow and is not required for this launcher.
