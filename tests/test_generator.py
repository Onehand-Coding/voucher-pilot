# In tests/test_generator.py

import pytest

from voucher_pilot.generator import VoucherGenerator


@pytest.fixture
def generator():
    """Provides a VoucherGenerator instance for testing."""
    return VoucherGenerator()


def test_generate_from_pattern(generator):
    """
    Tests if the pattern generator creates vouchers that match the
    exact structure and length of the provided pattern.
    """
    pattern = "L-N-l"
    count = 10
    vouchers = generator.generate_from_pattern(pattern, count)

    # Check if we got the correct number of vouchers
    assert len(vouchers) == count

    # Check if the first voucher matches the pattern's structure
    first_voucher = vouchers[0]
    assert len(first_voucher) == len(pattern)
    assert first_voucher[0].isupper()
    assert first_voucher[1] == "-"
    assert first_voucher[2].isdigit()
    assert first_voucher[3] == "-"
    assert first_voucher[4].islower()


def test_generate_random_combinations(generator):
    """
    Tests if the random generator creates vouchers with the correct
    length and character types.
    """
    length = 8
    num_digits = 3
    num_letters = 5
    count = 100
    charset = "abcdef"

    vouchers = generator.generate_random_combinations(length, num_digits, count, charset)

    assert len(vouchers) == count

    # Check if a sample voucher has the correct composition
    sample_voucher = vouchers[0]
    assert len(sample_voucher) == length

    letter_count = sum(1 for char in sample_voucher if char.isalpha())
    digit_count = sum(1 for char in sample_voucher if char.isdigit())

    assert letter_count == num_letters
    assert digit_count == num_digits


def test_generate_random_combinations_rejects_impossible_count(generator):
    """Requests larger than the possible unique space must fail fast, not hang."""
    with pytest.raises(ValueError, match="capacity"):
        generator.generate_random_combinations(2, 2, 91, "ab")


def test_generate_from_pattern_rejects_impossible_count(generator):
    with pytest.raises(ValueError, match="capacity"):
        generator.generate_from_pattern("L", 27)


def test_generate_from_pattern_rejects_literal_only_repeat(generator):
    with pytest.raises(ValueError, match="capacity"):
        generator.generate_from_pattern("ABX", 2)


def test_generate_rejects_non_positive_count(generator):
    with pytest.raises(ValueError, match="positive"):
        generator.generate_from_pattern("L", 0)


def test_chunk_all_combinations_writes_prefix_files(tmp_path):
    from voucher_pilot.generator import VoucherFileManager

    voucher_file = tmp_path / "all.txt"
    voucher_file.write_text("ABCD11\nABCD12\nABEF11\nABEF12\n")

    VoucherFileManager(voucher_file).chunk_file_for_all_combinations()

    chunk_dir = tmp_path / "all_chunks"
    assert (chunk_dir / "a" / "abcd.txt").read_text().splitlines() == ["ABCD11", "ABCD12"]
    assert (chunk_dir / "a" / "abef.txt").read_text().splitlines() == ["ABEF11", "ABEF12"]


def test_chunk_all_combinations_digits_only_falls_back(tmp_path):
    from voucher_pilot.generator import VoucherFileManager

    voucher_file = tmp_path / "all.txt"
    voucher_file.write_text("11\n12\n21\n")

    VoucherFileManager(voucher_file).chunk_file_for_all_combinations()

    chunk_dir = tmp_path / "all_chunks"
    assert (chunk_dir / "1.txt").read_text().splitlines() == ["11", "12"]
    assert (chunk_dir / "2.txt").read_text().splitlines() == ["21"]


def test_generate_random_accepts_exact_capacity(generator):
    vouchers = generator.generate_random_combinations(2, 1, 40, "ab")
    assert len(vouchers) == 40


def test_generate_random_rejects_duplicate_charset(generator):
    with pytest.raises(ValueError, match="unique"):
        generator.generate_random_combinations(3, 1, 2, "aab")


def test_generate_random_rejects_digit_overlap(generator):
    with pytest.raises(ValueError, match="overlap"):
        generator.generate_random_combinations(3, 1, 2, "a1")


def test_chunk_by_prefix_analysis_digits_only_falls_back(tmp_path):
    from voucher_pilot.generator import VoucherFileManager

    voucher_file = tmp_path / "random.txt"
    voucher_file.write_text("11\n12\n21\n")

    VoucherFileManager(voucher_file).chunk_file_by_prefix_analysis()

    chunk_dir = tmp_path / "random_chunks"
    assert (chunk_dir / "1.txt").read_text().splitlines() == ["11", "12"]
    assert (chunk_dir / "2.txt").read_text().splitlines() == ["21"]
