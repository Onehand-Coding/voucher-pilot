# VoucherPilot Hardening Design

Date: 2026-11-01
Status: Approved for implementation

## Context

VoucherPilot generates voucher candidates and tests them through a captive
portal with Selenium. It has two tests and no CI. Several real bugs exist:

- `generate_from_pattern` and `generate_random_combinations` can loop forever
  when the requested count exceeds the possible unique vouchers.
- `chunk_file_for_all_combinations` references an undefined
  `num_digits_to_replace`, so "all combinations" chunking is broken.
- `connect_vouchers` references `VoucherConnector.URL`, which does not exist, and
  can reference an unbound connector in `finally`.
- Runtime files and `.env` live in the project; the tool is dual-use and needs a
  clearer authorized-use gate.
- No Ruff config, no CI, and no CONTEXT.

## Goals

1. Make generator capacity explicit and fail fast with `ValueError`.
2. Fix all-combination chunking and add tests.
3. Fix connector URL/finally bugs.
4. Add an authorization confirmation before testing vouchers.
5. Add Ruff, pytest config, CI, README, `.env.example`, and CONTEXT.

## Design

- Add capacity helpers using `math.comb`, `math.factorial`, and `math.prod`:
  - random: `C(len(charset), num_letters) * C(10, num_digits) * factorial(length)`
  - pattern: product of the character-set sizes for `L/l/N/C` positions.
- Reject `count <= 0` and `count > capacity`.
- `chunk_file_for_all_combinations` extracts leading alphabetic prefixes with a
  regex instead of the broken numeric placeholder.
- `connect_vouchers` uses the connector instance URL, initializes the connector
  before `try`, and removes `sys.exit()` from `finally`.
- Add a confirmation prompt: type `yes` to confirm authorization before testing.
- Keep `.env` support for the hotspot URL and browser paths; add
  `.env.example` and document authorized use.
- CI uses `uv sync --extra test`, Ruff, format check, pytest, and wheel build.

## Acceptance

- Impossible generation requests raise instead of hanging.
- All-combination chunking writes chunk files.
- The connector no longer raises on the URL attribute or unbound variable.
- Unauthorized users are asked to confirm before any voucher testing.
- `ruff`, format, and `pytest` pass locally and in CI.
