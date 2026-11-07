"""ApexRig-AI GUI entry point.

The desktop GUI is the public application. CMD mode remains an internal
diagnostic/backend module and is intentionally not exposed in the startup flow.
"""
import subprocess
import sys
from pathlib import Path


def main():
    base = Path(__file__).resolve().parent
    script = base / "app.py"

    # Prefer pythonw.exe so the desktop app has no console window.
    python = Path(sys.executable).with_name("pythonw.exe")
    if not python.exists():
        python = Path(sys.executable)

    # Wait for the GUI to close so the TEMP bootstrap does not clean its files
    # while the application is still running.
    subprocess.run([str(python), str(script)], cwd=str(base), check=False)


if __name__ == "__main__":
    main()
