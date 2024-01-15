import logging
from pathlib import Path

PARENT_DIR = Path(__file__).parents[1]

LOGS_DIR = PARENT_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

VOUCHER_DIR = PARENT_DIR / 'vouchers'
VOUCHER_DIR.mkdir(exist_ok=True)


def configure_logging(log_level=logging.DEBUG):
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(LOGS_DIR / "logs.txt", mode='w'), logging.StreamHandler()],
    )


if __name__ == '__main__':
    pass
