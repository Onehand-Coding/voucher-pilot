# VoucherPilot

A Python automation tool for generating and testing voucher codes on captive
portal hotspots. It is intended for authorized testing only.

[![CI](https://github.com/Onehand-Coding/voucher-pilot/actions/workflows/ci.yml/badge.svg)](https://github.com/Onehand-Coding/voucher-pilot/actions/workflows/ci.yml)

## Authorized Use

Use VoucherPilot only on networks you own or have written permission to test.
The `connect` flow asks you to type `yes` to confirm authorization before it
starts testing vouchers. Do not use it against third-party networks.

## Features

- **Smart Voucher Generation**: Create wordlists with configurable length,
  character sets, and patterns.
- **Automatic Capacity Checks**: Impossible requests fail with `ValueError`
  instead of hanging.
- **Automated Testing**: Test vouchers with Selenium browser automation.
- **Browser Auto-Detection**: Finds common Chromium-based browsers, or use an
  explicit `CHROME_BINARY_PATH`.
- **File Chunking**: Split large wordlists by prefix for easier handling.

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv)
- A Chromium-based browser (Chrome, Brave, Chromium, etc.)

### Installation

```bash
git clone https://github.com/Onehand-Coding/voucher-pilot.git
cd voucher-pilot
uv sync
cp .env.example .env
# Edit .env with your hotspot URL and optional browser paths
```

### Usage

```bash
uv run voucher-pilot
```

Choose one of:

1. Generate voucher wordlists.
2. Test vouchers from a file or chunk directory.

## Configuration

Create `.env` from `.env.example`:

```env
# Required: hotspot login URL
URL="http://192.168.1.1/"

# Optional: explicit chromedriver path
# DRIVER_PATH="/usr/local/bin/chromedriver"

# Optional: explicit Chromium-based browser path
# CHROME_BINARY_PATH="/usr/bin/brave-browser"
```

The project root is discovered from `pyproject.toml`. Logs are written to
`logs/` and generated voucher files to `vouchers/`; both are ignored by Git.

## Generated Files

- `vouchers/*.txt`: generated voucher wordlists.
- `vouchers/*_chunks/`: chunked wordlists, possibly nested by first letter.
- `logs/voucher_pilot.log`: latest run log, rewritten each run.

## Development

```bash
uv sync --extra test
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv build
```

The test suite mocks Selenium, so no browser or real hotspot is required.

## Project Structure

```text
voucher-pilot/
├── src/voucher_pilot/
│   ├── cli.py          # Interactive CLI
│   ├── config.py       # Paths, .env configuration, logging
│   ├── connector.py    # Selenium voucher testing
│   └── generator.py    # Voucher generation and chunking
├── tests/
├── docs/superpowers/   # Hardening spec and plan
├── .github/workflows/  # CI
├── CONTEXT.md          # Project knowledge
└── pyproject.toml
```

## How It Works

1. **Generate**: Builds candidate vouchers from random, exhaustive, or pattern
   strategies. Capacity is checked before generation.
2. **Test**: Opens the configured hotspot URL, enters each voucher, and waits
   for a `Connected` status. Requests larger than the possible space are
   rejected.
3. **Results**: Logs attempts and stops when a voucher succeeds.

## Contributing

1. Fork the repository.
2. Create a feature branch.
3. Add tests for behavior changes.
4. Run `uv run ruff check .`, `uv run ruff format --check .`, and
   `uv run pytest`.
5. Open a pull request.

## License

MIT License. See [LICENSE](LICENSE).
