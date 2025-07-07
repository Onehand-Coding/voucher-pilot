import sys
import atexit
import shutil
import logging
from random import choice
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

from . import config


class VoucherConnector:
    def __init__(self):
        self.url = config.URL
        self.driver_path = config.DRIVER_PATH
        self.used_vouchers = []

    def get_driver(self):
        """
        Initializes the Selenium WebDriver, using a configured path
        or falling back to auto-detection.
        """
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")

        browser_path = config.CHROME_BINARY_PATH

        if browser_path:
            logging.info(f"Using configured browser path: {browser_path}")
            chrome_options.binary_location = browser_path
        else:
            logging.info("No configured browser path, attempting auto-detection...")
            known_browsers = ["brave-browser", "google-chrome", "chromium-browser"]
            for browser in known_browsers:
                path = shutil.which(browser)
                if path:
                    logging.info(f"Auto-detected browser: '{browser}' at {path}")
                    chrome_options.binary_location = path
                    break

        if not chrome_options.binary_location:
             logging.error("Could not find a browser. Please set CHROME_BINARY_PATH in your .env file.")
             raise Exception("Browser not found.")

        logging.info("Initializing WebDriver...")
        return webdriver.Chrome(options=chrome_options)

    def remove_used(self):
        if self.used_vouchers:
            logging.info("Removing used vouchers...")
            with FileInput(self.source_file, inplace=True) as vouchers:
                for voucher in vouchers:
                    if voucher.strip() not in self.used_vouchers:
                        print(voucher.strip(), end="\n")
            logging.info("Done!")

    def connect(self, voucher):
        logging.info(f"Trying to connect with voucher: {voucher}")
        driver = None  # Define driver here to ensure it's available in except blocks
        try:
            driver = self.get_driver()

            logging.info(f"Attempting to open URL: {self.url}")
            driver.get(self.url)
            logging.info("URL opened successfully. Searching for voucher input field...")

            # Find and interact with the voucher input field
            voucher_input = driver.find_element(By.ID, "voucherInput")
            logging.info("Voucher input field found.")
            voucher_input.clear()
            voucher_input.send_keys(voucher)

            # Find and click the connect button
            connect_button = driver.find_element(By.ID, "connectBtn")
            logging.info("Connect button found. Clicking to submit voucher...")
            connect_button.click()

            # Wait for the connection status to update
            logging.info("Waiting for connection status...")
            WebDriverWait(driver, 5).until(
                EC.text_to_be_present_in_element(
                    (By.ID, "connectionStatus"), "Connected"
                )
            )
        except TimeoutException:
            # This error is specific and expected
            logging.error(f"Connection failed with voucher '{voucher}': Timed out waiting for 'Connected' status.")
            if driver:
                driver.quit()
        except Exception as e:
            # This catches other potential errors during the process
            logging.error(f"An unexpected error occurred while processing voucher '{voucher}': {e}")
            if driver:
                driver.quit()
        except KeyboardInterrupt:
            logging.info("Connection attempt cancelled by user.")
            if driver:
                driver.quit()
            raise  # Re-raise the exception so the main loop can catch it
        else:
            # This block only runs if the try block completes without errors
            logging.info("Connection successful!")
            return driver
        finally:
            # This will always run
            self.used_vouchers.append(voucher)

    def connect_from_dir(self, voucher_source):
        for source in set(voucher_source.glob("*.txt")):
            self.source_file = source
            logging.info(f"Current source file: {self.source_file.name}")
            with open(self.source_file, "r") as vouchers:
                vouchers = [
                    voucher.strip()
                    for voucher in set(vouchers.readlines())
                    if voucher.strip()
                ][:10]
                for voucher in vouchers:
                    driver = self.connect(voucher)
                    if driver:
                        return driver
            self.remove_used()

    def connect_from_file(self, voucher_source):
        self.source_file = voucher_source
        logging.info(f"Current source file: {self.source_file.name}")
        with open(self.source_file, "r") as vouchers:
            vouchers = {voucher.strip() for voucher in vouchers if voucher.strip()}
            for voucher in vouchers:
                driver = self.connect(voucher)
                if driver:
                    return driver
        self.remove_used()

    def run(self):
        voucher_source = get_source()
        if voucher_source.is_dir():
            driver = self.connect_from_dir(voucher_source)
        else:
            driver = self.connect_from_file(voucher_source)
        if driver:
            return driver

        logging.error(
            "All vouchers failed. Unable to establish a successful connection."
        )
        return None


def get_source(voucher_dir=config.VOUCHER_DIR):
    voucher_sources = list(voucher_dir.glob("*"))

    def get_source_index():
        source_index = None
        source_indices = list(range(1, len(voucher_sources) + 1))
        while source_index not in source_indices:
            try:
                source_index = int(input("> "))
            except ValueError:
                continue
        return source_index - 1

    print("Choose voucher source")
    for index, file in enumerate(voucher_sources, start=1):
        print(index, file.name)

    voucher_source = voucher_sources[get_source_index()]

    if voucher_source.is_dir():
        print("Choose letters to use: ")
        while True:
            chosen_letter = input("> ")
            if not chosen_letter or not chosen_letter.isalpha():
                print("Enter a letter.")
                continue
            letter_directory = voucher_source / chosen_letter[0]
            if len(chosen_letter) == 1:
                return letter_directory

            source_files = list(letter_directory.glob("*.txt"))
            letters_count = len(
                [letter for letter in source_files[0].stem if letter.isalpha()]
            )
            if len(chosen_letter) > letters_count:
                print(f"Enter up to {letters_count} letters.")
                continue
            voucher_source = choice(
                [file for file in source_files if file.name.startswith(chosen_letter)]
            )
            if voucher_source.exists():
                break
            print(f"No matched file for letter {chosen_letter}.")

    return voucher_source


def connect_vouchers():
    config.configure_logging(logging.INFO)
    driver = None
    try:
        voucher_connector = VoucherConnector()
        driver = voucher_connector.run()
    except Exception as e:
        logging.error(f"An error occured, {e}")
    except KeyboardInterrupt:
        logging.info("Script terminated.")
    else:
        if driver:
            webbrowser.open(VoucherConnector.URL)
    finally:
        if driver:
            driver.quit()
        atexit.register(voucher_connector.remove_used)
        sys.exit()


if __name__ == "__main__":
    connect_vouchers()
