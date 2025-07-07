# In tests/test_connector.py

import pytest
from voucher_pilot.connector import VoucherConnector

def test_get_driver_with_configured_path(mocker):
    """
    Tests if get_driver correctly uses the binary_location from the config.
    The 'mocker' fixture is provided by pytest-mock.
    """
    # Mock the config to simulate having a browser path set
    mocker.patch('voucher_pilot.connector.config.CHROME_BINARY_PATH', '/usr/bin/test-browser')

    # Mock the entire webdriver.Chrome class
    mock_chrome = mocker.patch('voucher_pilot.connector.webdriver.Chrome')

    # Create an instance of our connector and call the method
    connector = VoucherConnector()
    connector.get_driver()

    # Assert that webdriver.Chrome was called with an options object
    # that has the correct binary_location set on it.
    mock_chrome.assert_called_once()
    call_args, call_kwargs = mock_chrome.call_args
    options_arg = call_kwargs.get('options')

    assert options_arg is not None
    assert options_arg.binary_location == '/usr/bin/test-browser'
