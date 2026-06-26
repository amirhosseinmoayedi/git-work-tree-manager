from __future__ import annotations

import argparse
from pathlib import Path

from .commands import cmd_create, cmd_doctor, cmd_info, cmd_list, cmd_remove, cmd_shell

def build_parser():
    p=argparse.ArgumentParser(prog="wtm", description="Git worktree and environment manager for agent workflows.")
    sub=p.add_subparsers(required=True)
    c=sub.add_parser("create"); c.add_argument("--repo", type=Path, required=True); c.add_argument("--config", type=Path); c.add_argument("--task", required=True); c.add_argument("--branch-type", default="chore"); c.add_argument("--agent", default="default"); c.add_argument("--base-ref"); c.add_argument("--approve-hooks", action="store_true"); c.add_argument("--launch"); c.set_defaults(func=cmd_create)
    l=sub.add_parser("list"); l.set_defaults(func=cmd_list)
    i=sub.add_parser("info"); i.add_argument("id"); i.set_defaults(func=cmd_info)
    s=sub.add_parser("shell"); s.add_argument("id"); s.set_defaults(func=cmd_shell)
    r=sub.add_parser("remove"); r.add_argument("id"); r.add_argument("--force", action="store_true"); r.add_argument("--delete-branch", action="store_true"); r.add_argument("--approve-hooks", action="store_true"); r.set_defaults(func=cmd_remove)
    d=sub.add_parser("doctor"); d.add_argument("--repo", type=Path); d.set_defaults(func=cmd_doctor)
    return p

def main(argv=None):
    args=build_parser().parse_args(argv); return args.func(args)

if __name__ == "__main__": main()
