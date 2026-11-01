import logging
import os
from pathlib import Path

from dotenv import load_dotenv


def find_project_root(marker_file="pyproject.toml"):
    """Find the project root, falling back to the current directory.

    Installed wheels do not ship a ``pyproject.toml``, so the search must not
    raise. In that case, runtime files go under the current working directory.
    """
    current_path = Path(__file__).resolve()
    for parent in current_path.parents:
        if (parent / marker_file).exists():
            return parent
    return Path.cwd()


PROJECT_ROOT = find_project_root()
LOGS_DIR = PROJECT_ROOT / "logs"
VOUCHER_DIR = PROJECT_ROOT / "vouchers"

LOGS_DIR.mkdir(exist_ok=True)
VOUCHER_DIR.mkdir(exist_ok=True)

load_dotenv()
URL = os.getenv("URL", "http://192.168.1.1/")
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
