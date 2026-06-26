# Repository Guidelines

## Project Structure & Module Organization
This is a Python CLI package for managing Git worktrees and per-worktree environments. Source code lives in `src/worktree_manager/`.

Key packages:
- `cli.py`: parser and entrypoint only.
- `commands.py`: command handlers for `create`, `list`, `info`, `shell`, `remove`, and `doctor`.
- `config/`: default config, user config, project `.worktree.yml` loading, and YAML fallback parsing.
- `git_backend/`: Git subprocess operations.
- `state/`: local registry persistence.
- `templating/`: variable rendering and filters such as `slug` and `db`.
- `runtime/`: resource allocation and status enrichment.
- `lifecycle/`: env file generation, marker files, and hooks.

Tests live in `tests/` and should mirror behavior, for example `tests/test_config.py` for config loading and `tests/test_cli.py` for parser behavior.

## Build, Test, And Development Commands
- `uv sync`: install runtime and development dependencies from `pyproject.toml` and `uv.lock`.
- `.venv/bin/python -m pytest -q`: run the local test suite.
- `uv tool install --editable /Users/amirhossein/Documents/git-work-tree-manager --force`: install `wtm` for normal use.
- `wtm --help` and `wtm create --help`: verify the installed CLI.

Use `WTM_REGISTRY=/tmp/wtm-test.db` for isolated registry tests. Shared worktrees default to `~/projects/.worktrees`; prefer `~/.config/worktree-manager/config.yml` over repeated shell exports.

## Coding Style & Naming Conventions
Use Python 3.10+ with 4-space indentation. Keep modules focused and avoid project-specific behavior in the manager. Billing, Django, and other target-repo setup belongs in that repo's `.worktree.yml` or hooks.

Use snake_case for functions, variables, and module names. CLI commands should stay short and action-oriented. Branch names should default to conventional-style prefixes, for example `chore/task-codex-01` or `fix/task-codex-01`.

## Testing Guidelines
Use pytest. Name test files `test_<behavior>.py` and tests `test_<expected_behavior>()`. Prefer temporary directories and isolated registry files.

Cover config loading, user config precedence, template filters, registry behavior, env generation, resource allocation, hook approval, and create/remove flows. For real project smoke tests, create a disposable worktree, verify generated files and commands, then remove the worktree and branch.

## Commit & Pull Request Guidelines
Follow Conventional Commits, matching the current history style, for example `chore: streamline git worktree management`.

Pull requests should include a short summary, test results, CLI/config changes, and known limitations. For changes touching generated files, hooks, branch naming, resource allocation, or cleanup, include a concrete smoke-test command and outcome.

## Security & Configuration Tips
Never print `.env` secrets or registry contents that may contain sensitive values. Project-defined hooks must remain opt-in through explicit approval. Treat `.worktree.yml` as configuration, not trusted code.
