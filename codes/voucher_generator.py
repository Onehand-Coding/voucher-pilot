import itertools
from pathlib import Path
from random import sample, shuffle
from string import ascii_letters, ascii_lowercase, ascii_uppercase, digits

# Create folder for wordlists
PARENT_DIR = Path(__file__).parents[1]
VOUCHER_DIR = PARENT_DIR / 'vouchers'
VOUCHER_DIR.mkdir(exist_ok=True)

# voucher files
RANDOM_VOUCHER = VOUCHER_DIR / 'random_combinations.txt'
ALL_COMBINATIONS_VOUCHER = VOUCHER_DIR / 'all_combinations.txt'
RESERVED_NAMES = ('prn', 'aux')


class VoucherGenerator:
    def __init__(self, file, letters, letter_case, word_length, num_digits, digits=digits):
        self.file = file.parent / f'{file.stem}_{letter_case}_{word_length}{file.suffix}'
        self.letters = letters
        self.letter_case = letter_case
        self.digits = digits
        self.word_length = word_length
        self.num_digits = num_digits
        self.voucher_num_id = '0' * self.num_digits

    def save_vouchers(self, vouchers):
        print(f'Saving generated words to {self.file.name}...')

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
        print(f'Breaking {self.file.name} voucher file into smaller file chunks...')

        file_directory = self.file.parent / f'{self.file.stem}_chunks'
        with open(self.file, 'r') as vouchers:
            for letters in self.get_voucher_filenames():
                letter_directory = file_directory / letters[0]
                letter_directory.mkdir(parents=True, exist_ok=True)
                letter_file = letter_directory / f'{letters}.txt'

                if letter_file.stem.lower() in RESERVED_NAMES:
                    letter_file = letter_directory / f'{letters}_res.txt'
                if letter_file.exists():
                    continue
                with open(letter_file, 'w') as out_file:
                    for voucher in vouchers:
                        if not voucher.strip().startswith(letters):
                            break
                        out_file.write(voucher)

    def generate_random_combinations(self, word_count):
        def generate_word(letters, digits, num_letters):
            digits = sample(digits, k=self.num_digits)
            letters = sample(letters, k=num_letters)
            voucher = letters + digits
            shuffle(voucher)
            return ''.join(voucher)

        num_letters = self.word_length - self.num_digits
        print(f'Generating {word_count} random vouchers...')
        vouchers = {generate_word(self.letters, self.digits, num_letters) for _ in range(word_count)}
        self.save_vouchers(vouchers)

    def generate_all_combinations(self):
        if not self.file.exists():
            num_letters = self.word_length - self.num_digits

            print(f'Generating {num_letters} {self.letter_case} letters + {self.num_digits} digits vouchers...')
            letters = (''.join(letters) for letters in itertools.product(self.letters, repeat=num_letters))
            numbers = (''.join(num) for num in itertools.product(self.digits, repeat=self.num_digits))
            vouchers = (letter + digit for letter, digit in itertools.product(letters, numbers))
            self.save_vouchers(vouchers)
            self.chunk_file()
            print('Done!')
        else:
            print(f'{self.file.name} Voucher file already exists!')


def get_number(task=''):
    print(task)
    number = ''
    while not number.isdigit():
        number = input('> ')
    return int(number)


def get_voucher_file():
    print(f'Choose voucher type to generate\n')
    voucher_files = {
        'random': RANDOM_VOUCHER,
        'all': ALL_COMBINATIONS_VOUCHER,
    }
    for wordlist_type, file in voucher_files.items():
        print(f'"{wordlist_type}" - will be saved to {file.stem}_<case>_<length>{file.suffix}')

    wordlist_type = None
    while wordlist_type not in voucher_files:
        wordlist_type = input('> ')
    return voucher_files[wordlist_type]


def get_letter_case(lower=ascii_lowercase, upper=ascii_uppercase, mixed=ascii_letters):
    print('Choose letter case to use\n')
    letters_case = {
        'lower': {'lower_case': lower},
        'upper': {'upper_case': upper},
        'mixed': {'mixed_case': mixed},
    }
    for key, case in letters_case.items():
        print(f'{key} - "{list(case.values())[0]}"')

    case = None
    while case not in letters_case:
        case = input('> ')
    (case, letters), = letters_case[case].items()
    return (letters, case)


def generate_voucher():
    print('Voucher generator\n')
    voucher_file = get_voucher_file()
    word_length = get_number('Enter word length')
    digit_count = get_number('Enter number of numeric characters to be added to word')
    letters, case = get_letter_case()
    generator = VoucherGenerator(voucher_file, letters, case, word_length, digit_count)

    generate = {
        RANDOM_VOUCHER: lambda: generator.generate_random_combinations(
            get_number('Enter number of random words to generate')
        ),
        ALL_COMBINATIONS_VOUCHER: lambda: generator.generate_all_combinations(),
    }.get(voucher_file)
    generate()


if __name__ == '__main__':
    generate_voucher()
