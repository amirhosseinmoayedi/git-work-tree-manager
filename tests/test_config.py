from worktree_manager.config import default_worktrees_root, load_config


def test_default_config_uses_unified_worktree_root(tmp_path, monkeypatch):
    monkeypatch.setenv("WTM_WORKTREES_ROOT", str(tmp_path / ".worktrees"))
    cfg = load_config(tmp_path / "billing")

    assert default_worktrees_root() == str(tmp_path / ".worktrees")
    assert cfg["worktrees"]["root"] == "${worktrees_root}/${project.name}"
    assert cfg["project"]["name"] == "billing"


def test_worktree_root_can_come_from_user_config(tmp_path, monkeypatch):
    user_config = tmp_path / "config.yml"
    user_config.write_text("worktrees_root: ~/custom-worktrees\n")
    monkeypatch.delenv("WTM_WORKTREES_ROOT", raising=False)
    monkeypatch.setenv("WTM_CONFIG", str(user_config))

    assert default_worktrees_root().endswith("/custom-worktrees")


def test_external_config_merges_with_defaults(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    config = tmp_path / "billing.worktree.yml"
    config.write_text(
        """
version: 1
project:
  name: billing
worktrees:
  root: ${worktrees_root}/billing
resources:
  ports:
    app:
      from: 8001
      to: 8099
""".strip()
    )

    cfg = load_config(repo, config)

    assert cfg["project"]["name"] == "billing"
    assert cfg["project"]["default_base_ref"] == "main"
    assert cfg["worktrees"]["root"] == "${worktrees_root}/billing"
    assert cfg["worktrees"]["id_template"] == "${task_slug}-${agent}-${counter}"
    assert cfg["worktrees"]["branch_template"] == "${branch_type}/${task_slug}-${agent}-${counter}"
    assert cfg["resources"]["ports"]["app"]["from"] == 8001
    assert cfg["env"]["output"] == ".env"
