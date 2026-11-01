import logging
import shutil

# control browser
import webbrowser
from fileinput import FileInput

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from . import config


class VoucherConnector:
    def __init__(self):
        self.url = config.URL
        self.driver_path = config.DRIVER_PATH
        self.source_file = None
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
            logging.error(
                "Could not find a browser. Please set CHROME_BINARY_PATH in your .env file."
            )
            raise Exception("Browser not found.")

        logging.info("Initializing WebDriver...")
        return webdriver.Chrome(options=chrome_options)

    def remove_used(self):
        if self.source_file is None:
            return
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
                EC.text_to_be_present_in_element((By.ID, "connectionStatus"), "Connected")
            )
        except TimeoutException:
            # This error is specific and expected
            logging.error(
                f"Connection failed with voucher '{voucher}': Timed out waiting for 'Connected' status."
            )
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
                    voucher.strip() for voucher in set(vouchers.readlines()) if voucher.strip()
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
        if not voucher_source:
            return None
        if voucher_source.is_dir():
            driver = self.connect_from_dir(voucher_source)
        else:
            driver = self.connect_from_file(voucher_source)
        if driver:
            return driver

        logging.error("All vouchers failed. Unable to establish a successful connection.")
        return None


def get_source(voucher_dir=config.VOUCHER_DIR):
    """
    Lets the user select a voucher source, intelligently handling both
    simple and complex (nested) chunking structures.
    """
    voucher_sources = list(voucher_dir.glob("*"))
    if not voucher_sources:
        print("Error: The 'vouchers' directory is empty.")
        print("Please use the 'generate' command to create a voucher file first.")
        return None

    def get_source_index():
        source_index = None
        source_indices = list(range(1, len(voucher_sources) + 1))
        while source_index not in source_indices:
            try:
                source_index = int(input("> "))
            except (ValueError, IndexError):
                continue
        return source_index - 1

    print("\nChoose voucher source:")
    for index, file in enumerate(voucher_sources, start=1):
        print(f"{index}: {file.name}")

    voucher_source = voucher_sources[get_source_index()]

    if not voucher_source.is_dir():
        return voucher_source

    print(f"\nSelected directory: {voucher_source.name}")

    is_simple_chunk_dir = any(
        item.is_file() and item.suffix == ".txt" for item in voucher_source.iterdir()
    )

    if is_simple_chunk_dir:
        print("This appears to be a directory of simple chunks.")
        print("Choose a starting letter to use:")
        chosen_letter = input("> ").lower().strip()

        target_file = voucher_source / f"{chosen_letter}.txt"
        if target_file.exists():
            return target_file
        else:
            print(f"Error: Chunk file '{target_file.name}' not found.")
            return None

    else:
        print("This appears to be a directory of nested chunks.")
        print(
            "Choose letters to use (e.g., 'a' for a full directory, or 'ab' for a specific file):"
        )

        while True:
            chosen_letter = input("> ").lower().strip()
            if not chosen_letter or not chosen_letter.isalpha():
                print("Invalid input. Please enter only letters.")
                continue

            letter_directory = voucher_source / chosen_letter[0]
            if not letter_directory.is_dir():
                print(f"No chunk directory found for letter '{chosen_letter[0]}'.")
                continue

            if len(chosen_letter) == 1:
                return letter_directory

            source_files = list(letter_directory.glob("*.txt"))
            if not source_files:
                print(f"No .txt files found in {letter_directory.name}")
                continue

            matched_file = next((f for f in source_files if f.name.startswith(chosen_letter)), None)

            if matched_file:
                return matched_file
            else:
                print(f"No matched file for prefix '{chosen_letter}' in {letter_directory.name}.")

    return voucher_source


def connect_vouchers():
    config.configure_logging(logging.INFO)
    print("Only use VoucherPilot on networks you own or are authorized to test.")
    if input("Type 'yes' to confirm authorization: ").strip().lower() != "yes":
        logging.info("Authorization not confirmed; exiting.")
        return

    driver = None
    voucher_connector = None
    try:
        voucher_connector = VoucherConnector()
        driver = voucher_connector.run()
    except Exception as e:
        logging.error(f"An error occured, {e}")
    except KeyboardInterrupt:
        logging.info("Script terminated.")
    else:
        if driver:
            webbrowser.open(voucher_connector.url)
    finally:
        if driver:
            driver.quit()
        if voucher_connector:
            voucher_connector.remove_used()


if __name__ == "__main__":
    connect_vouchers()
