from __future__ import annotations

import ast
from typing import Any


def loads(text: str) -> dict[str, Any]:
    root: dict[str, Any] = {}; stack=[(-1, root)]
    lines=text.splitlines(); i=0
    while i < len(lines):
        raw=lines[i].split('#',1)[0].rstrip('\n')
        if not raw.strip(): i+=1; continue
        indent=len(raw)-len(raw.lstrip(' ')); s=raw.strip()
        while stack and indent <= stack[-1][0]: stack.pop()
        parent=stack[-1][1]
        if s.startswith('- '):
            parent.append(_val(s[2:].strip()))
            i+=1; continue
        key, _, val=s.partition(':'); key=key.strip(); val=val.strip()
        if val == "":
            # lookahead list or dict
            j=i+1
            while j < len(lines) and not lines[j].strip(): j+=1
            child=[] if j < len(lines) and lines[j].lstrip().startswith('- ') else {}
            parent[key]=child; stack.append((indent, child))
        else:
            parent[key]=_val(val)
        i+=1
    return root


def _val(v: str) -> Any:
    if v in {"[]", "{}"}: return [] if v == "[]" else {}
    if v.lower() in {"true", "false"}: return v.lower()=="true"
    try: return ast.literal_eval(v)
    except Exception: pass
    try: return int(v)
    except ValueError: return v.strip('"\'')
