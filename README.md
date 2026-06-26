# worktree-manager

`worktree-manager` provides the `wtm` CLI for creating, inspecting, and safely removing Git worktrees with per-worktree environment files, resource allocation, and lifecycle hooks.

The manager is generic. Repository-specific setup belongs in each target repo's `.worktree.yml`, not in this project.

## Install

From a checkout, install dependencies and run the test suite:

```bash
uv sync
.venv/bin/python -m pytest -q
```

For day-to-day CLI use, install the editable package once from the checkout root:

```bash
uv tool install --editable . --force
wtm --help
```

From outside the checkout, pass the manager path explicitly:

```bash
uv tool install --editable /path/to/worktree-manager --force
```

## Configure

The local registry is an embedded Turso database. By default it lives at:

```text
~/.local/share/worktree-manager/registry.db
```

Override it only for tests or isolated runs:

```bash
WTM_REGISTRY=/tmp/wtm-test.db wtm list
```

Worktrees use one shared root. The built-in default is:

```text
~/projects/.worktrees
```

To make the setting explicit, create `~/.config/worktree-manager/config.yml`:

```yaml
worktrees_root: ~/projects/.worktrees
```

This keeps all generated worktrees outside the source repositories while still grouping them under one predictable location.

## Project Config

Each target repo owns its own `.worktree.yml`:

```yaml
version: 1

project:
  name: example-app
  default_base_ref: main

worktrees:
  root: "${worktrees_root}/${project.name}"
  id_template: "${task_slug}-${agent}-${counter}"
  branch_template: "${branch_type}/${task_slug}-${agent}-${counter}"

resources:
  ports:
    app:
      strategy: first_free
      from: 8001
      to: 8099
  env:
    DATABASE_NAME: "${project.name|db}_${worktree_id|db}"

env:
  source: .env
  output: .env
  overrides:
    DATABASE_NAME: "${resources.env.DATABASE_NAME}"
    APP_PORT: "${resources.ports.app}"
    WORKTREE_ID: "${worktree_id}"

hooks:
  pre_create: []
  post_create: []
  pre_remove: []
  post_remove: []
```

Commit project config in the target repo when the whole team should use it. Keep local-only overrides out of this manager repository.

## Usage

Create a worktree:

```bash
wtm create --repo /path/to/repo --task smoke-test --agent codex
```

By default, the branch is conventional-style:

```text
chore/smoke-test-codex-01
```

Use another conventional prefix when needed:

```bash
wtm create --repo /path/to/repo --task pricing-bug --branch-type fix --agent codex
```

Inspect and remove:

```bash
wtm list
wtm info smoke-test-codex-01
wtm remove smoke-test-codex-01 --force --delete-branch
```

## Project Smoke Test Pattern

Use this pattern from any target repo that has a `.worktree.yml`:

```bash
wtm create --repo /path/to/target-repo --task package-smoke --agent codex
wtm info package-smoke-codex-01
```

Confirm the generated files and allocated values:

```bash
cd ~/projects/.worktrees/example-app/package-smoke-codex-01
test -f .env
test -f WORKTREE.md
grep '^APP_PORT=' .env
grep '^DATABASE_NAME=' .env
grep '^WORKTREE_ID=' .env
```

Then run the target project's own setup, app check, representative tests, and cleanup commands. For example, a Docker-backed web app might use:

```bash
docker compose up -d db
./scripts/check-app
./scripts/test-smoke
docker compose down -v
wtm remove package-smoke-codex-01 --force --delete-branch
```

Keep these commands in the target repo's documentation or hooks when they are project-specific.

## Notes For Agents

Agents should use the installed `wtm` executable, not this repository's virtualenv path. If a target repo needs database creation, dev-server checks, or framework-specific setup, implement that in the target repo's `.worktree.yml`, scripts, or contributor guide.
