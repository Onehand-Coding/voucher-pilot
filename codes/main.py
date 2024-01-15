from voucher_generator import generate_vouchers
from voucher_connector import connect_vouchers


def main():
    print('connect or generate?')
    options = {
        'generate': lambda: generate_vouchers(),
        'connect': lambda: connect_vouchers(),
    }
    option = None
    while option not in options:
        option = input('> ').lower().strip()

    options[option]()


if __name__ == '__main__':
    main()
