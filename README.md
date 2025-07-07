# VoucherPilot ✈️

A Python automation tool for generating and testing voucher codes on captive portal hotspots.

## Features

- **Smart Voucher Generation** - Create custom wordlists with configurable length, character sets, and patterns
- **Automated Testing** - Systematically test vouchers using Selenium browser automation
- **Zero-Config Setup** - Auto-detects installed Chromium browsers (Chrome, Brave, etc.)
- **Modern Python Stack** - Built with `pyproject.toml`, `uv` package management, and clean `src/` layout
- **Flexible Configuration** - Environment-based config with `.env` file support

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- Chromium-based browser (Chrome, Brave, etc.)

### Installation

```bash
# Clone and navigate to project
git clone https://github.com/Onehand-Coding/voucher-pilot.git
cd voucher-pilot

# Install with uv
uv pip install -e .

# Create configuration file
cp .env.example .env
# Edit .env with your hotspot URL
```

### Usage

```bash
# Run the interactive CLI
voucher-pilot

# Choose between:
# 1. Generate voucher wordlists
# 2. Test vouchers against hotspot
```

## Configuration

Create a `.env` file in the project root:

```env
# Required: Your hotspot login URL
URL="http://175.1.1.1/"

# Leave this blank if chromedriver is in system's PATH.
# DRIVER_PATH="/usr/local/bin/chromedriver"
# Optional: Custom browser path
# CHROME_BINARY_PATH="/path/to/your/browser"
```

## Project Structure

```
voucher-pilot/
├── src/voucher_pilot/    # Main application code
│   ├── cli.py           # Command-line interface
│   ├── config.py        # Configuration management
│   ├── connector.py     # Browser automation logic
│   └── generator.py     # Voucher generation logic
├── vouchers/            # Generated voucher files
├── logs/               # Application logs
├── tests/               # Test suite
├── pyproject.toml      # Project configuration
└── .env               # Local environment settings
```

## How It Works

1. **Generate Phase**: Creates potential voucher codes based on common patterns and your specifications
2. **Test Phase**: Uses Selenium to automate browser interactions, systematically trying each voucher until a successful connection is established
3. **Results**: Logs all attempts and stops when a valid voucher is found

## Contributing

We welcome contributions! Please feel free to submit issues and pull requests.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**⚠️ Disclaimer**: This tool is for educational and authorized testing purposes only. Always ensure you have permission to test network systems.
