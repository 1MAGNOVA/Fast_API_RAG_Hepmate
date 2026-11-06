
import platform
import subprocess
import sys
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent
VENV_DIR = PROJECT_DIR / "venv"

SYSTEM = platform.system()


def check_platform():
    """Validate the supported operating systems."""

    if SYSTEM not in ("Darwin", "Windows"):
        raise RuntimeError(
            f"Unsupported operating system: {SYSTEM}"
        )

    print(f"[OK] Operating system: {SYSTEM}")


def check_python():
    """Validate the Python version."""

    version = sys.version_info

    if version < (3, 12):
        raise RuntimeError(
            "Python 3.12 or newer is required."
        )

    print(f"[OK] Python version: {version.major}.{version.minor}")


def create_virtual_environment():
    """Create the project virtual environment if missing."""

    if VENV_DIR.exists():
        print("[OK] Virtual environment already exists.")
        return

    print("[SETUP] Creating virtual environment...")

    subprocess.check_call([
        sys.executable,
        "-m",
        "venv",
        str(VENV_DIR),
    ])

    print("[OK] Virtual environment created.")


if __name__ == "__main__":
    check_platform()
    check_python()
    create_virtual_environment()
