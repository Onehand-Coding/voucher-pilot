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

    RESERVED_NAMES = ("prn", "aux")

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

    def _get_prefixes_from_file(self) -> set[str]:
        """Read the file and return the unique leading alphabetic prefixes."""
        logging.info(f"Extracting prefixes from {self.output_path.name}...")
        if not self.output_path.exists():
            return set()

        prefixes = set()
        with self.output_path.open("r") as f:
            for line in f:
                match = re.match(r"^([A-Za-z]+)", line.strip())
                if match:
                    prefixes.add(match.group(1))

        if not prefixes:
            logging.warning("Could not find alphabetic prefixes in the voucher file.")

        logging.info(f"Found {len(prefixes)} unique prefixes.")
        return prefixes

    def chunk_file_for_all_combinations(self):
        """
        Chunks the file using the specific logic for 'all' combinations,
        which relies on knowing all possible alphabetic prefixes.
        """
        chunk_directory = self.output_path.parent / f"{self.output_path.stem}_chunks"
        chunk_directory.mkdir(exist_ok=True)

        # Step 1: Extract prefixes from the file itself.
        prefixes = self._get_prefixes_from_file()

        # Step 2: Read the entire file into memory.
        with self.output_path.open("r") as f:
            vouchers_in_memory = f.readlines()

        # Step 3: Iterate through the extracted prefixes and write chunk files.
        for prefix in prefixes:
            if not prefix:
                continue

            letter_directory = chunk_directory / prefix[0]
            letter_directory.mkdir(parents=True, exist_ok=True)

            chunk_file_path = letter_directory / f"{prefix}.txt"
            if chunk_file_path.stem.lower() in self.RESERVED_NAMES:
                chunk_file_path = letter_directory / f"{prefix}_res.txt"

            vouchers_to_write = [v for v in vouchers_in_memory if v.strip().startswith(prefix)]

            if vouchers_to_write:
                with chunk_file_path.open("w") as out_file:
                    out_file.writelines(vouchers_to_write)

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

        # Discover all unique alphabetic prefixes by reading the file
        prefixes = set()
        with self.output_path.open("r") as f:
            for line in f:
                voucher = line.strip()
                if not voucher:
                    continue
                # Extract the non-digit part as the prefix
                prefix = "".join(filter(str.isalpha, voucher))
                if prefix:
                    prefixes.add(prefix)

        logging.info(f"Discovered {len(prefixes)} unique prefixes. Now chunking file...")

        # Now, perform the sophisticated chunking using these discovered prefixes
        chunk_directory = self.output_path.parent / f"{self.output_path.stem}_chunks"
        chunk_directory.mkdir(exist_ok=True)

        with self.output_path.open("r") as f:
            vouchers_in_memory = f.readlines()

        for prefix in prefixes:
            letter_directory = chunk_directory / prefix[0].lower()
            letter_directory.mkdir(parents=True, exist_ok=True)

            chunk_file_path = letter_directory / f"{prefix}.txt"
            if chunk_file_path.stem.lower() in self.RESERVED_NAMES:
                chunk_file_path = letter_directory / f"{prefix}_res.txt"

            vouchers_to_write = [v for v in vouchers_in_memory if v.strip().startswith(prefix)]

            if vouchers_to_write:
                with chunk_file_path.open("w") as out_file:
                    out_file.writelines(vouchers_to_write)

        logging.info("Analysis-based chunking complete!")
