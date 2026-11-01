import logging
import sys
from string import ascii_lowercase, ascii_uppercase

from . import config
from .connector import connect_vouchers

# Updated imports to use the new FileManager class
from .generator import VoucherFileManager, VoucherGenerator


def get_user_choice(prompt: str, options: dict) -> str:
    """Generic function to get a valid choice from the user."""
    print(prompt)
    for key, desc in options.items():
        print(f"- {key}: {desc}")

    choice = None
    while choice not in options:
        choice = input("> ").lower().strip()
    return choice


def get_number(prompt: str) -> int:
    """Generic function to get a valid integer from the user."""
    print(prompt)
    number_str = ""
    while not number_str.isdigit():
        number_str = input("> ")
    return int(number_str)


def handle_generate_vouchers():
    """Orchestrates the voucher generation process with threshold-based chunking."""
    config.configure_logging()
    generator = VoucherGenerator()

    # Define a threshold for offering to chunk files.
    CHUNK_OFFER_THRESHOLD = 10000

    strategy_choice = get_user_choice(
        "\nChoose a generation strategy:",
        {
            "random": "Generate vouchers with a specific number of letters/digits.",
            "all": "Generate all possible combinations (can be very large).",
            "pattern": "Generate vouchers from a specific pattern (e.g., LNN-LNN).",
        },
    )

    vouchers = []
    output_path = None
    file_manager = None
    num_letters = 0
    charset = ""
    count = 0  # Initialize count for later checks

    # --- Pattern Strategy ---
    if strategy_choice == "pattern":
        print("\n--- Pattern Generation ---")
        print("  L = Uppercase, l = lowercase, N = Number, C = Any. Others are literal.")
        print("  Example: 'lNN-LL' -> 'a12-BC'")

        pattern = input("\nEnter the voucher pattern: ")
        count = get_number("Enter number of vouchers to generate:")
        vouchers = generator.generate_from_pattern(pattern, count)

        safe_pattern_str = "".join(filter(str.isalnum, pattern))
        output_filename = f"pattern_{safe_pattern_str}_{count}.txt"
        output_path = config.VOUCHER_DIR / output_filename
        file_manager = VoucherFileManager(output_path)

    # --- Random or All Strategy ---
    else:
        length = get_number("Enter word length:")
        num_digits = get_number(f"Enter number of digits (0-{length}):")
        num_letters = length - num_digits

        case_choice_map = {
            "lower": ascii_lowercase,
            "upper": ascii_uppercase,
            "both": ascii_lowercase + ascii_uppercase,
        }
        case_choice = get_user_choice(
            "Choose letter case:", {k: f'"{v[:5]}..."' for k, v in case_choice_map.items()}
        )
        charset = case_choice_map[case_choice]

        base_name = "random" if strategy_choice == "random" else "all"
        output_filename = f"{base_name}_{case_choice}_{length}.txt"
        output_path = config.VOUCHER_DIR / output_filename
        file_manager = VoucherFileManager(output_path)

        if strategy_choice == "random":
            count = get_number("Enter number of random vouchers to generate:")
            vouchers = generator.generate_random_combinations(length, num_digits, count, charset)
        elif strategy_choice == "all":
            print("\n⚠️ WARNING: This can create very large files and take a long time.")
            if input("Continue? (y/n): ").lower() != "y":
                print("Generation cancelled.")
                return
            vouchers = generator.generate_all_combinations(num_letters, num_digits, charset)

    # --- Save and Intelligent Chunking ---
    if vouchers and file_manager:
        file_manager.save_vouchers(vouchers)
        print(f"\nSuccessfully created '{output_path.name}'.")

        should_offer_chunk = False
        if strategy_choice == "all":
            should_offer_chunk = True
        elif count > CHUNK_OFFER_THRESHOLD:
            print(f"\nNote: You've generated {count} vouchers, which can be a large file.")
            should_offer_chunk = True

        if should_offer_chunk:
            if input("Do you want to break this file into smaller chunks? (y/n): ").lower() == "y":
                if strategy_choice == "all":
                    # Call the specific chunker for 'all' combinations
                    file_manager.chunk_file_for_all_combinations()
                else:
                    # For large random/pattern files, offer the user a choice
                    chunk_type = get_user_choice(
                        "\nChoose a chunking method:",
                        {
                            "simple": "Chunk by the first letter of each voucher (e.g., 'a.txt', 'b.txt').",
                            "advanced": "Analyze all unique prefixes and chunk by them (e.g., 'abc.txt', 'def.txt').",
                        },
                    )
                    if chunk_type == "simple":
                        file_manager.chunk_file_generic()
                    elif chunk_type == "advanced":
                        file_manager.chunk_file_by_prefix_analysis()


def main():
    """The main entry point for the Voucher-Pilot application."""
    try:
        main_choice = get_user_choice(
            "Welcome to VoucherPilot! What would you like to do?",
            {"generate": "Generate new voucher files.", "connect": "Test vouchers from a file."},
        )
        if main_choice == "generate":
            handle_generate_vouchers()
        elif main_choice == "connect":
            connect_vouchers()

    except KeyboardInterrupt:
        print("\nExiting Voucher-Pilot. Goodbye! 👋")
        sys.exit(0)
    except Exception as e:
        logging.error(f"An unexpected error occurred in the main application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
