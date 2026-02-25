# Testing in Python

A short summary of what this project does.

## Installation

```bash
uv venv .venv
source .venv/bin/activate
uv pip install -e .
```

## uv cheatsheet

```bash
# Create a virtual environment
uv venv .venv

# Activate it (Linux/macOS)
source .venv/bin/activate

# Install your project in editable mode (like pip install -e .)
uv pip install -e .

# Add new packages
uv pip install rich

# Create a lock file (optional but recommended)
uv pip compile > requirements.txt
```

## Testing

Do

```bash
PYTHONPATH=src pytest
```

| Command                      | What it does                                            |
| ---------------------------- | ------------------------------------------------------- |
| pytest -v                    | Verbose output (shows test names, status)               |
| pytest -q                    | Quiet output (shows just test dots or status)           |
| pytest -v --tb=short         | Verbose with short tracebacks                           |
| pytest -v -rs                | Shows reason for skips/failures (not needed for passed) |
| pytest -v --disable-warnings | Hides warnings (but still shows passed tests)           |
| pytest -s -v                 | Shows print statements inside tests                     |

For tracebacks (the --tb argument), you can choose one of: auto, long, short, no, line, native.

## Linting

`mypy --strict --ignore-missing-imports .`

## Make using Nox

Define a noxfile.py. Then call `nox -s lint`.

## Original notes

See the private repo python-tests.
