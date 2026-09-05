"""The ``divejson`` command line."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from . import __version__
from .uddf import NonConformingOutputError, UddfError, convert_uddf
from .validate import DuplicateMemberError, parse_document, validate_document

# How many source locations one grouped finding names before it stops listing them. A
# habit of a whole file - eight dives with no UTC offset - is one finding, and the point
# of the line is the finding rather than the roll call.
_WHERES_SHOWN = 3

# The collections a converted document can carry, with how to count them.
_COUNTED = (("dives", "dive", "dives"), ("trips", "trip", "trips"), ("sites", "site", "sites"), ("gear", "gear item", "gear items"))


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

    convert = commands.add_parser(
        "convert",
        help="convert UDDF dive logs into DiveJSON",
        description=(
            "Reads each UDDF file and writes a DiveJSON document beside it, named after "
            "the input with a .divejson extension. Nothing the source did not record is "
            "filled in, and everything it did not carry is reported: those lines are the "
            "other half of the output, not a diagnostic. Exits non-zero if any file "
            "could not be converted."
        ),
    )
    convert.add_argument("files", nargs="+", type=Path, help="UDDF documents")
    convert.add_argument(
        "-o",
        "--output",
        type=Path,
        help="write the document here instead of beside the input; only with one input file",
    )
    convert.add_argument("-f", "--force", action="store_true", help="overwrite an existing output file")
    convert.add_argument(
        "--exported-at",
        type=_offset_aware,
        help="the document's exported_at, as an offset-aware date-time; defaults to now",
    )

    args = parser.parse_args(argv)
    if args.command == "convert":
        return _convert_command(args.files, args.output, force=args.force, exported_at=args.exported_at)
    return _validate_command(args.files)


def _offset_aware(text: str) -> datetime:
    """Parse `--exported-at`, which the format requires to carry a UTC offset (spec §5.2).

    It is the one member a converted document asserts about itself rather than about the
    source, so it is also the one thing that moves when the same file is converted twice.
    Being able to pin it is what makes two conversions of one input diffable — and what
    lets this repository's own fixture expectations be regenerated without every one of
    them churning a line that carries no information about the change.
    """
    normalized = text[:-1] + "+00:00" if text.endswith(("Z", "z")) else text
    try:
        value = datetime.fromisoformat(normalized)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{text!r} is not a date and time") from None
    if value.utcoffset() is None:
        raise argparse.ArgumentTypeError(f"{text!r} carries no UTC offset, which exported_at requires (spec §5.2)")
    return value


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


def _convert_command(
    files: list[Path], output: Path | None, *, force: bool, exported_at: datetime | None = None
) -> int:
    """Convert each UDDF file, writing the document to a file and the report to stdout.

    **The document goes to a file and never to stdout**, which is why there is no `-`
    destination. The report is the half of this command's output a diver has to read, and
    a converter that streamed the document down the same pipe would either bury it or
    force the report onto stderr, where nobody looks. `--output` names the file instead;
    an existing one is refused rather than silently replaced, since the obvious mistake is
    converting into a hand-written document's name.
    """
    if output is not None and len(files) > 1:
        print(f"--output names one file, but {len(files)} were given")
        return 1

    failed = False
    for path in files:
        destination = output if output is not None else path.with_suffix(".divejson")
        if destination == path:
            print(f"{path}: the output would overwrite the input; pass --output to name another file")
            failed = True
            continue
        try:
            data = path.read_bytes()
        except OSError as error:
            print(f"{path}: unreadable — {error}")
            failed = True
            continue
        try:
            conversion = convert_uddf(data, exported_at=exported_at)
        except NonConformingOutputError as error:
            # Not a property of the file: every way a source can be wrong is meant to
            # resolve to an omission and a note, so reaching here is this converter's bug.
            print(f"{path}: the converter produced a document that does not conform, which is a bug in it")
            for issue in error.issues:
                print(f"  {issue}")
            failed = True
            continue
        except UddfError as error:
            print(f"{path}: {error}")
            failed = True
            continue

        if destination.exists() and not force:
            print(f"{path}: {destination} already exists — pass --force to replace it, or --output to write elsewhere")
            failed = True
            continue
        try:
            destination.write_text(json.dumps(conversion.document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        except OSError as error:
            print(f"{path}: could not write {destination} — {error}")
            failed = True
            continue

        print(f"{path}: {_counted(conversion.document)} → {destination}")
        for message, wheres in conversion.grouped():
            print(f"  {_listed(wheres)}: {message}")
    return 1 if failed else 0


def _counted(document: dict) -> str:
    parts = []
    for member, singular, plural in _COUNTED:
        rows = document.get(member) or []
        if rows:
            parts.append(f"{len(rows)} {singular if len(rows) == 1 else plural}")
    return ", ".join(parts) if parts else "nothing the format carries"


def _listed(wheres: list[str]) -> str:
    if len(wheres) <= _WHERES_SHOWN:
        return ", ".join(wheres)
    return f"{', '.join(wheres[:_WHERES_SHOWN])} and {len(wheres) - _WHERES_SHOWN} more"


if __name__ == "__main__":
    sys.exit(main())
