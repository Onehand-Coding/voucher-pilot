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
    assert first_voucher[1] == '-'
    assert first_voucher[2].isdigit()
    assert first_voucher[3] == '-'
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
