from __future__ import annotations

import socket
from typing import Any
from .templates import render


def port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try: s.bind(("127.0.0.1", port)); return True
        except OSError: return False


def allocate(cfg: dict[str, Any], registry, values: dict[str, Any]) -> dict[str, Any]:
    resources={"ports": {}, "env": {}}
    used=registry.used_ports()
    for name, spec in cfg.get("resources", {}).get("ports", {}).items():
        if spec.get("strategy", "first_free") != "first_free": raise ValueError(f"unsupported port strategy for {name}")
        for p in range(int(spec.get("from", 8000)), int(spec.get("to", 8999))+1):
            if p not in used and port_free(p): resources["ports"][name]=p; used.add(p); break
        else: raise RuntimeError(f"no free port for {name}")
    merged={**values, "resources": resources}
    for name, tmpl in cfg.get("resources", {}).get("env", {}).items():
        resources["env"][name]=render(tmpl, merged)
    return resources
