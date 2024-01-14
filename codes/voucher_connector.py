import sys
import atexit
import logging
from fileinput import FileInput

# control browser
import webbrowser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from voucher_generator import PARENT_DIR, VOUCHER_DIR

# Setup logging
LOGS_DIR = PARENT_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOGS_DIR / "logs.txt", mode='w'), logging.StreamHandler()],
)

URL = "http://175.1.1.1/"
DRIVER_PATH = "C:/coding/python/tools/chromedriver-win64/chromedriver"


class VoucherConnector:
    def __init__(self, url, driver_path, source_dir):
        self.url = url
        self.driver_path = driver_path
        self.voucher_sources = list(source_dir.glob("*"))
        self.used_vouchers = []

    def get_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")

        return webdriver.Chrome(service=Service(self.driver_path), options=chrome_options)

    def remove_used(self):
        if self.used_vouchers:
            logging.info("Removing used vouchers...")
            with FileInput(self.source_file, inplace=True) as vouchers:
                for voucher in vouchers:
                    if voucher.strip() not in self.used_vouchers:
                        print(voucher.strip(), end="\n")
            logging.info("Done!")

    def get_source_index(self):
        source_index = None
        source_indices = list(range(1, len(self.voucher_sources) + 1))
        while source_index not in source_indices:
            try:
                source_index = int(input("> "))
            except ValueError:
                continue
        return source_index - 1

    def get_source(self):
        print("Choose voucher source")
        for index, file in enumerate(self.voucher_sources, start=1):
            print(index, file.name)

        voucher_source = self.voucher_sources[self.get_source_index()]

        if voucher_source.is_dir():
            print("Choose what letter to use: ")
            while True:
                chosen_letter = input("> ")
                if not chosen_letter or not chosen_letter.isalpha():
                    print("Enter a letter.")
                    continue
                voucher_source = voucher_source / chosen_letter
                break

        return voucher_source

    def connect(self, voucher):
        logging.info(f"Trying to connect with voucher: {voucher}")
        driver = self.get_driver()
        driver.get(self.url)

        voucher_input = driver.find_element(By.ID, "voucherInput")
        voucher_input.clear()
        voucher_input.send_keys(voucher)
        driver.find_element(By.ID, "connectBtn").click()
        try:
            WebDriverWait(driver, 5).until(
                EC.text_to_be_present_in_element((By.ID, "connectionStatus"), "Connected")
            )
        except TimeoutException:
            logging.error(f"Connection failed with voucher {voucher}. Retrying with another voucher.")
            driver.quit()
        except Exception as e:
            logging.error(f"An error occurred while connecting with voucher {voucher}: {e}")
            driver.quit()
        except KeyboardInterrupt:
            raise
        else:
            logging.info("Connection successful!")
            return driver
        finally:
            self.used_vouchers.append(voucher)

    def run(self):
        voucher_source = self.get_source()
        if voucher_source.is_dir():
            for source in set(voucher_source.glob('*.txt')):
                self.source_file = source
                print(source)
                with open(source, "r") as vouchers:
                    x = 0
                    vouchers_to_use = []
                    for voucher in (vouchers):
                        x += 1
                        vouchers_to_use.append(voucher.strip())
                        if x == 10:
                            break
                    for voucher in vouchers_to_use:
                        self.connect(voucher)
                self.remove_used()
        else:
            with open(self.source_file, "r") as vouchers:
                vouchers = {voucher.strip() for voucher in vouchers if voucher.strip()}
                for voucher in self.vouchers:
                    self.connect(voucher)

        logging.error("All vouchers failed. Unable to establish a successful connection.")
        return None


def connect_vouchers():
    driver = None
    try:
        voucher_connector = VoucherConnector(URL, DRIVER_PATH, VOUCHER_DIR)
        driver = voucher_connector.run()
    except Exception as e:
        logging.error(f"An error occured, {e}")
    except KeyboardInterrupt:
        logging.info("Script terminated.")
    else:
        if driver:
            webbrowser.open(URL)
    finally:
        if driver:
            driver.quit()
        atexit.register(voucher_connector.remove_used)
        sys.exit()


if __name__ == "__main__":
    connect_vouchers()
