"""The ``divejson`` command line."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .validate import DuplicateMemberError, parse_document, validate_document


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="divejson",
        description="Tools for DiveJSON, an open dive-log interchange format.",
    )
    parser.add_argument("--version", action="version", version=f"divejson {__version__}")
    commands = parser.add_subparsers(dest="command", required=True)

    validate = commands.add_parser(
        "validate",
        help="validate documents against the DiveJSON spec",
        description=(
            "Validates each file against the DiveJSON JSON Schema and the semantic "
            "requirements the schema cannot express. Exits non-zero if any file fails."
        ),
    )
    validate.add_argument("files", nargs="+", type=Path, help="DiveJSON documents")

    args = parser.parse_args(argv)
    return _validate_command(args.files)


def _validate_command(files: list[Path]) -> int:
    failed = False
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
            document = parse_document(text)
        except (OSError, UnicodeDecodeError) as error:
            print(f"{path}: unreadable — {error}")
            failed = True
            continue
        except DuplicateMemberError as error:
            print(f"{path}: 1 error")
            print(f"  $: {error}")
            failed = True
            continue
        except json.JSONDecodeError as error:
            print(f"{path}: 1 error")
            print(f"  $: not valid JSON — {error}")
            failed = True
            continue

        issues = validate_document(document, raw=text)
        if issues:
            failed = True
            print(f"{path}: {len(issues)} error{'s' if len(issues) != 1 else ''}")
            for issue in issues:
                print(f"  {issue}")
        else:
            print(f"{path}: OK")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
