#!/usr/bin/env python3
"""3AM fridge text — a smart fridge texts its owner at 3am.

Run with no arguments to write the one-line entry to
$MAKEFUN_OUTPUT_DIR/entry.txt (default /output/entry.txt).
--check only checks the line against the brief's gate
(1-140 characters, one line, valid UTF-8). --self-test checks
the line and a write/read round-trip in a throwaway directory.
"""

import os
import sys
import tempfile

TEXT = (
    "It's 3am. My door's been open 47 seconds, my light is on, and the "
    "leftovers behind the milk expired Tuesday. I counted. I always count."
)

LIMIT = 140


def gate(text):
    """Fail loudly unless the line fits the brief."""
    if not text.strip():
        raise SystemExit("refusing to ship a blank entry")
    if len(text) > LIMIT:
        raise SystemExit(f"entry is {len(text)} chars, limit is {LIMIT}")
    if text.count("\n") or text.count("\r"):
        raise SystemExit("entry must fit on one line")
    text.encode("utf-8")


def emit(text, directory):
    """Write the line with no trailing newline, then prove the
    file on disk holds exactly that line."""
    gate(text)
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, "entry.txt")
    with open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(text)
    with open(path, "rb") as handle:
        raw = handle.read()
    if raw != text.encode("utf-8"):
        raise SystemExit("entry.txt on disk does not match the entry line")
    try:
        on_disk = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise SystemExit("entry.txt on disk is not valid UTF-8")
    gate(on_disk)  # the file itself must pass the gate, not just the source
    return path


def run(argv):
    gate(TEXT)
    if "--check" in argv:
        print(f"check passed: {len(TEXT)} chars, inside the 1-{LIMIT} gate")
        return 0
    if "--self-test" in argv:
        with tempfile.TemporaryDirectory() as tmp:
            emit(TEXT, tmp)
        print(f"self-test passed: {len(TEXT)} chars round-tripped cleanly")
        return 0
    path = emit(TEXT, os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    print(f"wrote {len(TEXT)} chars to {path}")
    return 0


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
