from voucher_generator import generate_voucher
from voucher_connector import connect_vouchers


def main():
    print('connect or generate?')
    get_option = {
        'generate': lambda: generate_voucher(),
        'connect': lambda: connect_vouchers(),
    }.get(input('> ').strip())
    get_option()


if __name__ == '__main__':
    main()
