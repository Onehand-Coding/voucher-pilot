import itertools
import logging
import random
import re
from math import comb, factorial, prod
from pathlib import Path
from random import sample, shuffle
from string import ascii_lowercase, ascii_uppercase, digits


class VoucherGenerator:
    """Generates voucher data."""

    def generate_random_combinations(
        self, length: int, num_digits: int, count: int, charset: str
    ) -> list[str]:
        logging.info(f"Generating {count} random vouchers...")
        if count <= 0:
            raise ValueError("Count must be a positive integer.")

        num_letters = length - num_digits
        if length <= 0 or num_letters < 0 or num_digits < 0:
            raise ValueError("Length must be positive and digits cannot exceed length.")
        if len(charset) < num_letters or len(digits) < num_digits:
            raise ValueError("Character set is smaller than required for unique generation.")
        if len(set(charset)) != len(charset):
            raise ValueError("Character set must contain unique characters.")
        if set(charset) & set(digits):
            raise ValueError("Character set must not overlap with digits.")

        capacity = (
            comb(len(charset), num_letters) * comb(len(digits), num_digits) * factorial(length)
        )
        if count > capacity:
            raise ValueError(f"Cannot generate {count} unique vouchers; capacity is {capacity}.")

        vouchers = set()
        while len(vouchers) < count:
            letter_part = sample(charset, k=num_letters)
            digit_part = sample(digits, k=num_digits)
            voucher_list = letter_part + digit_part
            shuffle(voucher_list)
            vouchers.add("".join(voucher_list))
        return list(vouchers)

    def generate_all_combinations(
        self, num_letters: int, num_digits: int, charset: str
    ) -> itertools.product:
        logging.info("Preparing iterator for all combinations...")
        letters_iter = itertools.product(charset, repeat=num_letters)
        numbers_iter = itertools.product(digits, repeat=num_digits)
        return (
            "".join(letters) + "".join(numbers)
            for letters, numbers in itertools.product(letters_iter, numbers_iter)
        )

    def generate_from_pattern(self, pattern: str, count: int) -> list[str]:
        """Generates a list of unique vouchers based on a character pattern."""
        logging.info(f"Generating {count} vouchers from pattern: {pattern}")

        char_map = {
            "L": ascii_uppercase,
            "l": ascii_lowercase,
            "N": digits,
            "C": ascii_lowercase + ascii_uppercase + digits,
        }

        if count <= 0:
            raise ValueError("Count must be a positive integer.")

        capacity = prod(len(char_map[c]) for c in pattern if c in char_map)
        if capacity == 0:
            capacity = 1
        if count > capacity:
            raise ValueError(
                f"Cannot generate {count} unique vouchers from pattern; capacity is {capacity}."
            )

        vouchers = set()
        while len(vouchers) < count:
            voucher = []
            for char_code in pattern:
                if char_code in char_map:
                    # Append a random character from the corresponding set
                    voucher.append(random.choice(char_map[char_code]))
                else:
                    # Append the character literally (e.g., a hyphen '-')
                    voucher.append(char_code)
            vouchers.add("".join(voucher))

        return list(vouchers)


class VoucherFileManager:
    """Handles all file operations."""

    RESERVED_NAMES = {
        "prn",
        "aux",
        "con",
        "nul",
        *(f"com{i}" for i in range(1, 10)),
        *(f"lpt{i}" for i in range(1, 10)),
    }

    def __init__(self, output_path: Path):
        self.output_path = output_path

    def save_vouchers(self, vouchers: iter):
        logging.info(f"Saving generated vouchers to {self.output_path.name}...")
        count = 0
        with self.output_path.open("w") as f:
            for voucher in vouchers:
                f.write(voucher + "\n")
                count += 1
        logging.info(f"Successfully saved {count} vouchers.")

    def chunk_file_for_all_combinations(self):
        """Chunk an all-combinations file by its leading alphabetic prefix."""
        if not self.output_path.exists():
            logging.error(f"Cannot chunk file, as it does not exist: {self.output_path}")
            return

        chunk_directory = self.output_path.parent / f"{self.output_path.stem}_chunks"
        chunk_directory.mkdir(exist_ok=True)

        grouped_vouchers: dict[str, list[str]] = {}
        with self.output_path.open("r") as f:
            for line in f:
                voucher = line.strip()
                if not voucher:
                    continue
                match = re.match(r"^([A-Za-z]+)", voucher)
                if match:
                    grouped_vouchers.setdefault(match.group(1).lower(), []).append(line)

        if not grouped_vouchers:
            logging.warning(
                "No alphabetic prefixes found; falling back to first-character chunking."
            )
            self.chunk_file_generic()
            return

        for prefix, lines in grouped_vouchers.items():
            letter_directory = chunk_directory / prefix[0]
            letter_directory.mkdir(parents=True, exist_ok=True)

            chunk_file_path = letter_directory / f"{prefix}.txt"
            if prefix in self.RESERVED_NAMES:
                chunk_file_path = letter_directory / f"{prefix}_res.txt"

            with chunk_file_path.open("w") as out_file:
                out_file.writelines(lines)

        logging.info("File chunking complete!")

    def chunk_file_generic(self):
        """
        Chunks any voucher file by grouping lines based on their first character.
        This is suitable for 'random' or 'pattern' generated files.
        """
        if not self.output_path.exists():
            logging.error(f"Cannot chunk file, as it does not exist: {self.output_path}")
            return

        logging.info(f"Chunking '{self.output_path.name}' by first letter...")
        chunk_directory = self.output_path.parent / f"{self.output_path.stem}_chunks"
        chunk_directory.mkdir(exist_ok=True)

        # Use a dictionary to hold lists of vouchers for each starting letter
        grouped_vouchers = {}
        with self.output_path.open("r") as f:
            for line in f:
                voucher = line.strip()
                if not voucher:
                    continue
                first_char = voucher[0].lower()
                if first_char not in grouped_vouchers:
                    grouped_vouchers[first_char] = []
                grouped_vouchers[first_char].append(line)  # Keep the newline

        # Write each group to its own file
        for first_char, lines in grouped_vouchers.items():
            # No need for sub-sub-directories here, simplifying the structure
            chunk_file_path = chunk_directory / f"{first_char}.txt"
            with chunk_file_path.open("w") as out_file:
                out_file.writelines(lines)

        logging.info("Generic chunking complete!")

    def chunk_file_by_prefix_analysis(self):
        """
        Chunks a file by first analyzing it to discover all unique
        alphanumeric prefixes within the vouchers. This is ideal for
        large, complex 'random' or 'pattern' generated files.
        """
        if not self.output_path.exists():
            logging.error(f"Cannot chunk file, as it does not exist: {self.output_path}")
            return

        logging.info(f"Analyzing '{self.output_path.name}' to discover prefixes for chunking...")

        # Group by discovered alphabetic prefix in a single pass.
        grouped_vouchers: dict[str, list[str]] = {}
        with self.output_path.open("r") as f:
            for line in f:
                voucher = line.strip()
                if not voucher:
                    continue
                prefix = "".join(filter(str.isalpha, voucher)).lower()
                if prefix:
                    grouped_vouchers.setdefault(prefix, []).append(line)

        logging.info(f"Discovered {len(grouped_vouchers)} unique prefixes. Now chunking file...")

        chunk_directory = self.output_path.parent / f"{self.output_path.stem}_chunks"
        chunk_directory.mkdir(exist_ok=True)

        for prefix, lines in grouped_vouchers.items():
            letter_directory = chunk_directory / prefix[0]
            letter_directory.mkdir(parents=True, exist_ok=True)

            chunk_file_path = letter_directory / f"{prefix}.txt"
            if prefix in self.RESERVED_NAMES:
                chunk_file_path = letter_directory / f"{prefix}_res.txt"

            with chunk_file_path.open("w") as out_file:
                out_file.writelines(lines)

        logging.info("Analysis-based chunking complete!")
