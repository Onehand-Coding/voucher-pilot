# VoucherPilot Context

## Purpose

VoucherPilot is an interactive Python tool for generating voucher candidates and
testing them against a captive portal with Selenium. It is dual-use: the tool
must only be used on networks the operator owns or is authorized to test.

## Architecture

- `src/voucher_pilot/cli.py`: interactive prompts and orchestration.
- `src/voucher_pilot/generator.py`: voucher generation, capacity checks, and
  file chunking.
- `src/voucher_pilot/connector.py`: Selenium browser automation and voucher
  testing.
- `src/voucher_pilot/config.py`: project root discovery, `.env` loading, paths,
  and logging.

Generated files live in `vouchers/`; logs live in `logs/`. Both are ignored and
created at import time by `config.py`.

## Commands

```bash
uv sync --extra test          # install runtime and test dependencies
uv run voucher-pilot          # run the interactive CLI
uv run ruff check .           # lint
uv run ruff format --check .  # format check
uv run pytest                 # tests (Selenium is mocked)
uv build                      # build sdist/wheel
```

## Conventions

- Target Python 3.11+.
- Keep generation pure and testable; I/O belongs in `VoucherFileManager` or the
  CLI.
- Generator functions raise `ValueError` for impossible requests instead of
  looping or silently returning partial data.
- Tests use `pytest` and `pytest-mock`; no real browser or network is required.
- Do not add a comment for every line; match the existing short docstring style.

## Decisions

- **Capacity checks use combinatorics.** Random generation capacity is
  `C(len(charset), num_letters) * C(10, num_digits) * length!`. The charset must
  contain unique characters and must not contain digits, otherwise the formula
  would overcount. Pattern capacity is the product of the character-set sizes
  for `L`, `l`, `N`, and `C` positions. Literal positions do not expand the
  space.
- **Chunking extracts leading alphabetic prefixes with a regex and one pass.**
  The previous implementation depended on a numeric placeholder and referenced
  an undefined variable, so all-combination chunking always failed. Chunk
  directories and file names are lowercased so `get_source` can find them.
  Digits-only files fall back to first-character chunking.
- **The connector uses the instance URL.** `connect_vouchers` previously read a
  nonexistent `VoucherConnector.URL` class attribute and could reference an
  unbound connector in `finally`.
- **Authorization is explicit.** `connect_vouchers` requires typing `yes` before
  any voucher testing. This is a safety gate, not authentication.
- **Configuration stays in `.env`.** `URL`, `DRIVER_PATH`, and
  `CHROME_BINARY_PATH` are read by `config.py`; `.env.example` documents them.
  `DRIVER_PATH` is passed to Selenium as an explicit `Service`.
- **Installed wheels fall back to the current directory.** `pyproject.toml` is
  not shipped in the wheel, so `find_project_root` returns `Path.cwd()` when no
  marker is found. Runtime files are created there.
- **Logs do not include voucher values.** The connector logs progress without
  the candidate code so successful vouchers are not persisted in the log.

## Gotchas

- `generate_all_combinations` returns a lazy generator. The CLI streams it into
  the output file, but callers must not assume a list.
- Pattern `C` means any alphanumeric character; `L`, `l`, and `N` mean uppercase,
  lowercase, and digit. Other characters are literal. A pattern with no wildcard
  positions has capacity 1.
- `connect_from_dir` tests at most 10 vouchers per file in the current
  implementation.
- A voucher is only added to `used_vouchers` after the connect button is
  clicked. Browser startup failures therefore leave the source file untouched.
- All-combination chunks are named by lowercase prefix: `all_chunks/a/abcd.txt`.
- `remove_used` rewrites the current source file when testing finishes. It is a
  no-op if no source file was set.
- Selenium is pinned to `4.8.3`; changing it may affect driver management and the
  mocked tests.
- `.env` is ignored by Git; never commit real hotspot credentials.
