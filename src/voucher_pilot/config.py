import logging
import os
from pathlib import Path

from dotenv import load_dotenv


def find_project_root(marker_file="pyproject.toml"):
    """
    Locates the project root directory by searching for a marker file.

    Starts from the directory of the current script and moves upwards
    until the marker file (e.g., 'pyproject.toml') is found.
    """
    current_path = Path(__file__).resolve()
    for parent in current_path.parents:
        if (parent / marker_file).exists():
            return parent
    raise FileNotFoundError(f"Project root not found. Could not find '{marker_file}'.")


PROJECT_ROOT = find_project_root()
LOGS_DIR = PROJECT_ROOT / "logs"
VOUCHER_DIR = PROJECT_ROOT / "vouchers"

LOGS_DIR.mkdir(exist_ok=True)
VOUCHER_DIR.mkdir(exist_ok=True)

load_dotenv()
URL = os.getenv("URL", "http://175.1.1.1/")
DRIVER_PATH = os.getenv("DRIVER_PATH")
CHROME_BINARY_PATH = os.getenv("CHROME_BINARY_PATH")


def configure_logging(log_level=logging.DEBUG):
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(LOGS_DIR / "voucher_pilot.log", mode="w"),
            logging.StreamHandler(),
        ],
    )
