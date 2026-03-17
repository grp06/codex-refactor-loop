#!/usr/bin/env python3

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 2:
        raise SystemExit("usage: fake_codex_cli.py <record-path> [args...]")

    record_path = Path(sys.argv[1])
    forwarded = sys.argv[2:]
    record_path.write_text(
        json.dumps({"argv": forwarded, "cwd": os.getcwd()}),
        encoding="utf-8",
    )

    if forwarded[:2] == ["login", "status"]:
        print("Logged in using ChatGPT")
    elif forwarded and forwarded[0] == "logout":
        print("Logged out")
    else:
        print("Successfully logged in")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
