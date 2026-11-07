# ApexRig-AI

A dark, monochrome Windows desktop performance companion for monitoring RAM, CPU and processes, with optional Gemini-assisted recommendations.

## One-command online boot (Windows)

Open PowerShell and paste this single command:

```powershell
irm https://raw.githubusercontent.com/godofgamerz2013-ui/RAMAGEDON-FIXER/main/ONE-CLICK-BOOT.ps1 | iex
```

This downloads the latest public `main.zip`, extracts it to a temporary directory, copies the project to `%LOCALAPPDATA%\ApexRig-AI`, and runs the included `boot.ps1`. The project launcher creates/reuses a local `.venv`, installs requirements with `python -m pip`, and starts the app. Python 3.12 (64-bit) is supported for local source runs.

**Trust note:** This command downloads and executes a PowerShell script from this public repository. Review [ONE-CLICK-BOOT.ps1](https://github.com/godofgamerz2013-ui/RAMAGEDON-FIXER/blob/main/ONE-CLICK-BOOT.ps1) before running it. Run only when you trust the repository contents.

## Requirements

- Windows 10 or Windows 11, 64-bit
- Python 3.12 (64-bit), available as `python` on PATH
- Internet access for downloading the repository and installing Python packages

## Troubleshooting

- **Missing `src\app.py` or `requirements.txt`:** The bootstrap checks for both and stops with an explicit error. The complete app source must be committed to the repository before boot can work.
- **Python not found:** Install Python 3.12 (64-bit), enable its PATH option, then reopen PowerShell.
- **PowerShell or Application Control blocks script/package execution:** Follow your device administrator's approved policy. Do not bypass organizational security controls.
- **Dependency installation fails:** Check internet access and the error reported by `python -m pip`.

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

- `ONE-CLICK-BOOT.ps1` — download/extract/install/launch bootstrap
- `boot.ps1` — local project launcher
- `src/app.py` — desktop interface
- `src/engine.py` — monitoring, AI advice and safety checks
- `src/startup.py` — Windows startup integration
- `requirements.txt` — Python dependencies
- `.github/workflows/` — automated Windows build

## License

See [LICENSE](LICENSE).
