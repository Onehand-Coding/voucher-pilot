import sys
from .generator import generate_vouchers
from .connector import connect_vouchers


def main():
    """The main entry point for the VoucherPilot application."""
    try:
        print("connect or generate?")
        options = {
            "generate": lambda: generate_vouchers(),
            "connect": lambda: connect_vouchers(),
        }
        option = None
        while option not in options:
            option = input("> ").lower().strip()

        options[option]()

    except KeyboardInterrupt:
        print("\nExiting Voucher-Pilot. Goodbye! 👋")
        sys.exit(0)


if __name__ == "__main__":
    main()
