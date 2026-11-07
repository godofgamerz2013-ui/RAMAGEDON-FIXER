# ApexRig-AI

A dark, monochrome Windows desktop performance companion for monitoring RAM, CPU and processes, with optional Gemini-assisted recommendations.

> **Current status:** source project. A Windows installer is not included yet. The first compiled installer will be published separately under **GitHub Releases** when it is ready.

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
- Python **3.11 (64-bit)** for the reproducible build
- Internet connection for installing Python packages and optional Gemini access

## Run from source

Open PowerShell in the repository folder:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python src\app.py
```

Enter your Gemini API key inside the app if you want AI recommendations. Do not commit API keys, tokens, or personal configuration files.

## Build the Windows EXE yourself

### Option A — Build the standalone application (no installer)

1. Install Python 3.11 (64-bit).
2. Open PowerShell in the repository root.
3. Run:

```powershell
py -3.11 -m venv .build-venv
.\.build-venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt pyinstaller
pyinstaller --noconfirm --clean --windowed --name ApexRig-AI --paths src src\app.py
```

4. Your executable will be at:

```
dist\ApexRig-AI\ApexRig-AI.exe
```

### Option B — Build the setup installer

1. Install Python 3.11 (64-bit) and [Inno Setup 6](https://jrsoftware.org/isinfo.php).
2. Open PowerShell in the repository root.
3. Run:

```powershell
powershell -ExecutionPolicy Bypass -File installer\build_windows.ps1
```

4. The installer will be generated in the `dist` folder.

> The build must run on Windows. PyInstaller does not cross-compile a Windows executable when run on Linux or macOS.

## Build using GitHub Actions

1. Push the source to the public repository.
2. Open the repository's **Actions** tab.
3. Select **Build Windows installer**.
4. Click **Run workflow** and wait for the run to finish successfully.
5. Download the `ApexRig-AI-Windows-Installer` artifact from the run's **Artifacts** section.

The workflow creates a Windows installer on a GitHub-hosted Windows runner. The workflow artifact is for testing; the versioned installer will later be attached to a GitHub Release.

## Releases

Compiled installers will be published on the [Releases page](https://github.com/godofgamerz2013-ui/RAMAGEDON-FIXER/releases). Until a release asset appears there, download the source and build it using the instructions above.

## Project structure

- `src/app.py` — desktop interface
- `src/engine.py` — monitoring, AI advice and safety checks
- `src/startup.py` — Windows startup integration
- `requirements.txt` — Python dependencies
- `installer/` — Windows installer configuration and build script
- `.github/workflows/` — automated Windows build

## License

See [LICENSE](LICENSE).
