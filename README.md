# ApexRig-AI

A dark, monochrome Windows desktop performance companion for monitoring RAM, CPU and processes, with optional Gemini-assisted recommendations.

> **Current status:** source project. No compiled Windows installer is published yet. A versioned installer will be attached to **GitHub Releases** after a successful Windows build and validation.

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

## Requirements

- Windows 10 or Windows 11, 64-bit
- Python **3.12 (64-bit) is supported for local source testing**. The GitHub Actions build uses Python 3.11 for a consistent packaged build.
- Internet connection for installing Python packages and optional Gemini access

## Download and extract the source

Download the repository ZIP using **Code → Download ZIP** and extract it. Open PowerShell in the extracted project folder — the folder must contain `requirements.txt` and a `src` directory.

Do **not** run commands from Downloads unless the project has actually been extracted there. Adjust this example to the folder created by Windows:

```powershell
cd "$env:USERPROFILE\Downloads\ApexRig-AI"
Get-ChildItem
```

## Run from source (Python 3.12)

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python src\app.py
```

If activation is blocked for the current PowerShell session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

You can also avoid activation and invoke the environment directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe src\app.py
```

### Troubleshooting

**`py -3.11` says “No suitable Python runtime found”**  
Python 3.11 is not installed or detected by the launcher. For local testing, use `python -m venv .venv` with your installed Python 3.12. Run `py --list` to inspect detected runtimes.

**`pip.exe` is blocked by Windows Application Control**  
Use `python -m pip` or `.\.venv\Scripts\python.exe -m pip` instead of calling `pip.exe` directly. If the policy also blocks pip modules, use an administrator-approved installation route; do not attempt to bypass the policy.

**`uninstall-no-record-file` while upgrading pip**  
Do not upgrade global pip just to run this project. Create the virtual environment first and install requirements using its interpreter. If its pip is damaged, recreate the venv after checking the base Python installation.

**`can't open file ... src\\app.py`**  
You are not in the extracted project root. Run `Get-ChildItem` and confirm both `requirements.txt` and `src` exist before launching.

Enter your Gemini API key inside the app for AI recommendations. Do not commit API keys, tokens, or personal configuration files.

## Build the Windows EXE yourself

Windows builds must run on Windows; PyInstaller does not cross-compile Windows executables from Linux or macOS.

For the reproducible local build, install Python 3.11 (64-bit), then run from the project root:

```powershell
py -3.11 -m venv .build-venv
.\.build-venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt pyinstaller
pyinstaller --noconfirm --clean --windowed --name ApexRig-AI --paths src src\app.py
```

The executable is generated under `dist\ApexRig-AI\ApexRig-AI.exe`.

## Build using GitHub Actions

1. Open the repository's **Actions** tab.
2. Select **Build Windows application**.
3. Click **Run workflow** (or push a version tag beginning with `v`).
4. Download the `ApexRig-AI-Windows-EXE` artifact after a successful run.

The workflow uploads a ZIP containing the PyInstaller application folder. It is a test build artifact, not an installer.

## Releases

Validated release assets will be published on the [Releases page](https://github.com/godofgamerz2013-ui/RAMAGEDON-FIXER/releases). Until an asset appears there, download the source and build it using the instructions above.

## Project structure

- `src/app.py` — desktop interface
- `src/engine.py` — monitoring, AI advice and safety checks
- `src/startup.py` — Windows startup integration
- `requirements.txt` — Python dependencies
- `.github/workflows/` — automated Windows build

## License

See [LICENSE](LICENSE).
