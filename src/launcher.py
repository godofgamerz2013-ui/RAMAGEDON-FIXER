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

    # Prefer pythonw.exe so launching the desktop app does not create a console.
    python = Path(sys.executable).with_name("pythonw.exe")
    if not python.exists():
        python = Path(sys.executable)

    subprocess.Popen(
        [str(python), str(script)],
        cwd=str(base),
        close_fds=True,
    )


if __name__ == "__main__":
    main()
