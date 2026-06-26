from worktree_manager.cli import build_parser


def test_create_defaults_to_conventional_branch_type():
    args = build_parser().parse_args(["create", "--repo", "/tmp/repo", "--task", "fix price"])

    assert args.branch_type == "chore"


def test_create_accepts_branch_type():
    args = build_parser().parse_args(["create", "--repo", "/tmp/repo", "--task", "fix price", "--branch-type", "fix"])

    assert args.branch_type == "fix"
