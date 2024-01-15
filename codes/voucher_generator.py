import logging
import itertools
from pathlib import Path
from random import sample, shuffle
from string import ascii_lowercase, ascii_uppercase, digits

from configs import VOUCHER_DIR, configure_logging
# voucher files
RANDOM_VOUCHER_FILE = VOUCHER_DIR / 'random_combinations.txt'
ALL_COMBINATIONS_VOUCHER_FILE = VOUCHER_DIR / 'all_combinations.txt'
RESERVED_NAMES = ('prn', 'aux')


class VoucherGenerator:
    def __init__(self, file, letters, letter_case, word_length, num_digits, digits=digits[1:]):
        self.file = file.parent / f'{file.stem}_{letter_case}_{word_length}{file.suffix}'
        self.letters = letters
        self.letter_case = letter_case
        self.digits = digits
        self.word_length = word_length
        self.num_digits = num_digits
        self.voucher_num_id = '1' * self.num_digits

    def save_vouchers(self, vouchers):
        logging.info(f'Saving generated words to {self.file.name}...')

        with open(self.file, 'w') as f:
            for voucher in vouchers:
                f.write(voucher + '\n')

    def get_voucher_filenames(self):
        with open(self.file, 'r') as f:
            voucher_filenames = [
                word.strip().replace(self.voucher_num_id, '')
                for word in f
                if word.strip().endswith(self.voucher_num_id)
            ]
        return voucher_filenames

    def chunk_file(self):
        logging.info(f'Breaking {self.file.name} voucher file into smaller file chunks...')

        file_directory = self.file.parent / f'{self.file.stem}_chunks'
        with open(self.file, 'r') as voucher_file:
            vouchers = voucher_file.readlines()

            for letters in self.get_voucher_filenames():
                letter_directory = file_directory / letters[0]
                letter_directory.mkdir(parents=True, exist_ok=True)
                letter_file = letter_directory / f'{letters}.txt'

                if letter_file.stem.lower() in RESERVED_NAMES:
                    letter_file = letter_directory / f'{letters}_res.txt'

                if not letter_file.exists():
                    vouchers_to_write = [voucher for voucher in vouchers if voucher.strip().startswith(letters)]
                    with open(letter_file, 'w') as out_file:
                        for voucher in vouchers_to_write:
                            out_file.write(voucher)

    def generate_random_combinations(self, word_count):
        def generate_word(letters, digits, num_letters):
            digits = sample(digits, k=self.num_digits)
            letters = sample(letters, k=num_letters)
            voucher = letters + digits
            shuffle(voucher)
            return ''.join(voucher)

        self.num_letters = self.word_length - self.num_digits

        logging.info(f'Generating {word_count} random vouchers...')
        vouchers = {generate_word(self.letters, self.digits, self.num_letters) for _ in range(word_count)}
        self.save_vouchers(vouchers)

    def generate_all_combinations(self):
        if self.file.exists():
            self.file = new_filepath(self.file, add_prefix='_set')

        self.num_letters = self.word_length - self.num_digits

        logging.info(f'Generating {self.num_letters} {self.letter_case} letters + {self.num_digits} digits vouchers...')
        letters = (''.join(letters) for letters in itertools.product(self.letters, repeat=self.num_letters))
        numbers = (''.join(num) for num in itertools.product(self.digits, repeat=self.num_digits))
        vouchers = (letter + digit for letter, digit in itertools.product(letters, numbers))
        self.save_vouchers(vouchers)
        self.chunk_file()
        logging.info('Done!')


def new_filepath(file, *, parent=None, add_prefix='', start_count=1):
    base_path = Path(parent).absolute() / file if parent else file
    if add_prefix:
        start_count += 1
    new_path = base_path.parent / f'{base_path.stem}{add_prefix}({start_count}){base_path.suffix}'

    while new_path.exists():
        start_count += 1
        new_path = base_path.parent / f'{base_path.stem}{add_prefix}({start_count}){base_path.suffix}'

    return new_path


def get_number(task=''):
    print(task)
    number = ''
    while not number.isdigit():
        number = input('> ')
    return int(number)


def get_voucher_file():
    print(f'Choose voucher type to generate\n')
    voucher_files = {
        'random': RANDOM_VOUCHER_FILE,
        'all': ALL_COMBINATIONS_VOUCHER_FILE,
    }
    for wordlist_type, file in voucher_files.items():
        print(f'"{wordlist_type}" - will be saved to {file.stem}_<case>_<length>{file.suffix}')

    wordlist_type = None
    while wordlist_type not in voucher_files:
        wordlist_type = input('> ')
    return voucher_files[wordlist_type]


def get_letter_case(lower=ascii_lowercase, upper=ascii_uppercase):
    print('Choose letter case to use\n')
    letters_case = {
        'lower': {'lower_case': lower},
        'upper': {'upper_case': upper},
    }
    for key, case in letters_case.items():
        print(f'{key} - "{list(case.values())[0]}"')

    case = None
    while case not in letters_case:
        case = input('> ')
    (case, letters), = letters_case[case].items()
    return (letters, case)


def generate_vouchers():
    configure_logging()
    print('Voucher generator\n')
    voucher_file = get_voucher_file()
    word_length = get_number('Enter word length')
    digit_count = get_number('Enter number of numeric characters to be added to word')
    letters, case = get_letter_case()
    generator = VoucherGenerator(voucher_file, letters, case, word_length, digit_count)

    generate = {
        RANDOM_VOUCHER_FILE: lambda: generator.generate_random_combinations(
            get_number('Enter number of random words to generate')
        ),
        ALL_COMBINATIONS_VOUCHER_FILE: lambda: generator.generate_all_combinations(),
    }.get(voucher_file)
    generate()


if __name__ == '__main__':
    generate_vouchers()
