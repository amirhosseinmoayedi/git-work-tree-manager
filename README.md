# worktree-manager

`worktree-manager` provides the `wtm` CLI for creating, listing, inspecting, entering, and safely removing Git worktrees with per-worktree environment files, resources, and lifecycle hooks.

The registry is stored in a local embedded Turso database via `pyturso`; no Turso Cloud URL, token, or network access is required. Override the local registry file with `WTM_REGISTRY=/path/to/registry.db`.

```bash
wtm create --repo /path/to/repo --task smoke-test --agent codex
wtm list
wtm info smoke-test-codex-01
wtm remove smoke-test-codex-01 --force --delete-branch
```

Each target repository can define a `.worktree.yml` with path/branch templates, resource allocation, env overrides, and hooks.
