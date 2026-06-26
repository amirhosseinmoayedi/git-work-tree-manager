# worktree-manager

`worktree-manager` provides the `wtm` CLI for creating, inspecting, and safely removing Git worktrees with per-worktree environment files, resource allocation, and lifecycle hooks.

The manager is generic: repository-specific setup belongs in each target repo's `.worktree.yml`, not in this project.

## Install

For local development:

```bash
uv sync
.venv/bin/python -m pytest -q
```

For day-to-day CLI use, install the editable package once:

```bash
uv tool install --editable /Users/amirhossein/Documents/git-work-tree-manager --force
wtm --help
```

This installs `wtm` into the user tool path, so agents do not need to run it through this repository's `.venv`.

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

## Project Config

Each target repo owns its own `.worktree.yml`:

```yaml
version: 1

project:
  name: billing
  default_base_ref: main

worktrees:
  root: "${worktrees_root}/billing"
  id_template: "${task_slug}-${agent}-${counter}"
  branch_template: "${branch_type}/${task_slug}-${agent}-${counter}"

resources:
  ports:
    app:
      strategy: first_free
      from: 8001
      to: 8099
  env:
    DATABASE_NAME: "billing_${worktree_id|db}"

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

## Billing Smoke Test

Create a real billing worktree:

```bash
wtm create --repo /Users/amirhossein/projects/work/billing --task package-smoke --agent codex
```

Expected output path:

```text
~/projects/.worktrees/billing/package-smoke-codex-01
```

Inside the generated worktree:

```bash
cd ~/projects/.worktrees/billing/package-smoke-codex-01
grep '^APP_PORT=' .env
grep '^DATABASE_NAME=' .env
grep '^WORKTREE_ID=' .env
docker compose up -d db
docker compose exec -T db createdb -U user "$(grep '^DATABASE_NAME=' .env | cut -d= -f2)"
. scripts/set_env.sh
/Users/amirhossein/projects/work/billing/.venv/bin/python manage.py check
/Users/amirhossein/projects/work/billing/.venv/bin/python -m pytest core/tests/test_admin.py -q
/Users/amirhossein/projects/work/billing/.venv/bin/python -m pytest accountant/tests/test_timezone.py -q
```

Optional dev-server probe:

```bash
. scripts/set_env.sh
/Users/amirhossein/projects/work/billing/.venv/bin/python manage.py runserver 127.0.0.1:${APP_PORT}
curl -I http://127.0.0.1:${APP_PORT}/
```

Clean up:

```bash
docker compose down -v
wtm remove package-smoke-codex-01 --force --delete-branch
```
