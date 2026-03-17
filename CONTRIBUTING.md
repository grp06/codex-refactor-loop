# Contributing

## Setup

1. Clone this repository.
2. Clone the open-source Codex repository separately.
3. Set `CODEX_WORKSPACE` to the Codex Rust workspace path, or pass `--codex-workspace` when running commands.

Example:

```bash
export CODEX_WORKSPACE=/path/to/codex/codex-rs
```

## Development

Run the test suite from the repository root:

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

The project depends on the bundled skills in `.agents/skills`. If you change the workflow, keep those skills in sync with the CLI behavior.

## Repository Hygiene

- Keep local run logs out of version control. `runs/` should only retain `.gitkeep`.
- Avoid hardcoded machine-specific paths in code, tests, or docs.
- Keep the CLI noninteractive unless there is a clear reason to change that contract.
