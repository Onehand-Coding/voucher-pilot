# In tests/test_connector.py

from voucher_pilot.connector import VoucherConnector


def test_get_driver_with_configured_path(mocker):
    """
    Tests if get_driver correctly uses the binary_location from the config.
    The 'mocker' fixture is provided by pytest-mock.
    """
    # Mock the config to simulate having a browser path set
    mocker.patch("voucher_pilot.connector.config.CHROME_BINARY_PATH", "/usr/bin/test-browser")

    # Mock the entire webdriver.Chrome class
    mock_chrome = mocker.patch("voucher_pilot.connector.webdriver.Chrome")

    # Create an instance of our connector and call the method
    connector = VoucherConnector()
    connector.get_driver()

    # Assert that webdriver.Chrome was called with an options object
    # that has the correct binary_location set on it.
    mock_chrome.assert_called_once()
    call_args, call_kwargs = mock_chrome.call_args
    options_arg = call_kwargs.get("options")

    assert options_arg is not None
    assert options_arg.binary_location == "/usr/bin/test-browser"


def test_connect_vouchers_requires_authorization(mocker):
    from voucher_pilot.connector import connect_vouchers

    mocker.patch("builtins.input", return_value="no")
    connector_cls = mocker.patch("voucher_pilot.connector.VoucherConnector")

    connect_vouchers()

    connector_cls.assert_not_called()


def test_connect_vouchers_opens_connector_url(mocker):
    from voucher_pilot.connector import connect_vouchers

    driver = mocker.Mock()
    connector = mocker.Mock()
    connector.url = "http://example.test/"
    connector.run.return_value = driver
    mocker.patch("voucher_pilot.connector.VoucherConnector", return_value=connector)
    mocker.patch("builtins.input", return_value="yes")
    open_mock = mocker.patch("voucher_pilot.connector.webbrowser.open")

    connect_vouchers()

    open_mock.assert_called_once_with("http://example.test/")
    driver.quit.assert_called_once()
    connector.remove_used.assert_called_once()


def test_connect_from_file_keeps_vouchers_when_browser_fails(tmp_path, mocker):
    from voucher_pilot.connector import VoucherConnector

    source = tmp_path / "vouchers.txt"
    source.write_text("AAAA\nBBBB\n")
    connector = VoucherConnector()
    mocker.patch.object(connector, "get_driver", side_effect=RuntimeError("no browser"))

    connector.connect_from_file(source)

    assert source.read_text().splitlines() == ["AAAA", "BBBB"]


def test_remove_used_without_source_is_safe():
    from voucher_pilot.connector import VoucherConnector

    VoucherConnector().remove_used()


def test_get_driver_uses_configured_driver_path(mocker):
    from voucher_pilot.connector import VoucherConnector

    mocker.patch("voucher_pilot.connector.config.DRIVER_PATH", "/usr/bin/chromedriver")
    mocker.patch("voucher_pilot.connector.config.CHROME_BINARY_PATH", "/usr/bin/test-browser")
    mock_service = mocker.patch("voucher_pilot.connector.Service")
    mock_chrome = mocker.patch("voucher_pilot.connector.webdriver.Chrome")

    VoucherConnector().get_driver()

    mock_service.assert_called_once_with(executable_path="/usr/bin/chromedriver")
    assert mock_chrome.call_args.kwargs["service"] is mock_service.return_value


def test_get_source_finds_uppercase_chunk(tmp_path, mocker):
    from voucher_pilot.connector import get_source

    chunk_dir = tmp_path / "chunks"
    chunk_dir.mkdir()
    (chunk_dir / "ABCD.txt").write_text("ABCD11\n")
    mocker.patch("builtins.input", side_effect=["1", "abcd"])

    assert get_source(tmp_path) == chunk_dir / "ABCD.txt"
