# ApexRig-AI

A dark, monochrome Windows desktop performance companion for monitoring RAM, CPU and processes, with optional Gemini-assisted recommendations.

## Quick boot (Windows)

1. Download **Code → Download ZIP** and extract the complete repository.
2. Open PowerShell in the extracted folder (the folder containing `requirements.txt` and `src\app.py`).
3. Run this single command:

```powershell
.\boot.ps1
```

The launcher creates/reuses `.venv`, installs dependencies using `python -m pip`, and starts the app. No manual environment activation is needed. Python 3.12 (64-bit) is supported for local source runs.

If PowerShell blocks script execution for this session, run once:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then run `.\boot.ps1`.

> **Important:** Extract the ZIP first. Do not run the command from the Downloads folder unless that folder itself contains `boot.ps1`, `requirements.txt`, and `src\app.py`. This repository must contain the application source; the launcher cannot start files that have not been included in the extracted project.

## Requirements

- Windows 10 or Windows 11, 64-bit
- Python 3.12 (64-bit) for local source testing
- Internet access for dependency installation and optional Gemini AI features

## Troubleshooting

- **`requirements.txt` or `src\app.py` not found:** You are not in the extracted project root, or the source archive is incomplete. Extract the complete project and confirm both paths exist.
- **Python not found:** Install Python 3.12 (64-bit), ensure it is on PATH, then reopen PowerShell.
- **Dependency install blocked:** The launcher invokes pip as a Python module rather than calling `pip.exe`. If Windows Application Control blocks Python package installation too, use an administrator-approved installation route.
- **Virtual environment permission error:** Close Python processes using this project's `.venv`; remove the project's `.venv` folder only after confirming no process is using it, then rerun the launcher.

## Features

- RAM, CPU and process monitoring
- Gemini recommendations (advisory only)
- Local safety validation before process cleanup
- Dark, Light and System appearance modes
- Hardware telemetry

### Safety and limitations

- Gemini does not receive unrestricted authority to terminate processes.
- Review recommendations before enabling cleanup. Automatic cleanup and force termination should remain disabled unless you understand the consequences.
- Hardware features are telemetry-only in this version. No CPU/GPU clock, voltage, BIOS or firmware changes are performed.
- Closing applications can cause unsaved work to be lost.

## Build the Windows EXE

A Windows build must run on Windows; PyInstaller does not cross-compile Windows executables from Linux or macOS.

For a reproducible local build, install Python 3.11 (64-bit), then run from the project root:

```powershell
py -3.11 -m venv .build-venv
.\.build-venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt pyinstaller
pyinstaller --noconfirm --clean --windowed --name ApexRig-AI --paths src src\app.py
```

The executable is generated under `dist\ApexRig-AI\ApexRig-AI.exe`.

## GitHub Actions build

Open **Actions → Build Windows application → Run workflow**. A successful run uploads a ZIP artifact named `ApexRig-AI-Windows-EXE`. This is a test build artifact, not an installer.

## Releases

Validated release assets will be published on the [Releases page](https://github.com/godofgamerz2013-ui/RAMAGEDON-FIXER/releases).

## Project structure

- `boot.ps1` — one-command Windows launcher
- `src/app.py` — desktop interface
- `src/engine.py` — monitoring, AI advice and safety checks
- `src/startup.py` — Windows startup integration
- `requirements.txt` — Python dependencies
- `.github/workflows/` — automated Windows build

## License

See [LICENSE](LICENSE).
