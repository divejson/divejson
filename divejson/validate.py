"""Validation of DiveJSON documents.

Two passes, mirroring §3 of the specification: the JSON Schema (types, required members,
enums, ranges, lengths, and the structural rules like Position objects), then the
semantic requirements the schema cannot express — identifier uniqueness, referential
closure, cross-member arithmetic, profile-series integrity and span, the offset
requirement on ``exported_at``, and the member-order rule checked against the raw text.

Null is not a spelling of absence in this format (spec §5.4): the schema rejects it, so
the semantic checks below simply treat a missing member as missing.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import best_match

from . import SPEC_VERSION


@dataclass
class Issue:
    path: str
    message: str

    def __str__(self) -> str:
        return f"{self.path or '$'}: {self.message}"


class DuplicateMemberError(ValueError):
    """A JSON object in the input carries the same member name twice (spec §9)."""


def _reject_duplicate_members(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    obj: dict[str, Any] = {}
    for key, value in pairs:
        if key in obj:
            raise DuplicateMemberError(f"duplicate member name {key!r}")
        obj[key] = value
    return obj


def parse_document(text: str) -> Any:
    """Parse document text as JSON, rejecting duplicate member names."""
    return json.loads(text, object_pairs_hook=_reject_duplicate_members)


def load_document(path: Path) -> Any:
    with open(path, encoding="utf-8") as handle:
        return parse_document(handle.read())


def load_schema() -> dict[str, Any]:
    """Locate the packaged schema, falling back to the repository layout."""
    candidates = [
        Path(__file__).resolve().parent / "_schema" / "divejson.schema.json",
        Path(__file__).resolve().parent.parent / "schema" / "1.0" / "divejson.schema.json",
    ]
    for candidate in candidates:
        if candidate.is_file():
            with open(candidate, encoding="utf-8") as handle:
                return json.load(handle)
    raise FileNotFoundError("divejson.schema.json not found in package or repository")


def validate_document(doc: Any, raw: str | None = None) -> list[Issue]:
    """Validate one parsed document; an empty result means conforming.

    ``raw`` is the document's original text, used for the one rule that is about the
    bytes rather than the data: `format` first, `version` second (spec §4).
    """
    if not isinstance(doc, dict):
        return [Issue("$", "a DiveJSON document is a JSON object")]

    issues: list[Issue] = []

    declared = doc.get("version")
    if isinstance(declared, str) and declared != SPEC_VERSION:
        issues.append(
            Issue(
                "version",
                f"declares version {declared!r}; this validator implements {SPEC_VERSION} "
                "(readers tolerate newer minors per spec §5.6, validators do not)",
            )
        )
        major = declared.split(".", 1)[0]
        if major != SPEC_VERSION.split(".", 1)[0]:
            return issues

    if raw is not None:
        issues.extend(_member_order_issues(raw))
    issues.extend(_schema_issues(doc))
    issues.extend(_semantic_issues(doc))
    return issues


_FIRST_MEMBER = re.compile(r'^\s*\{\s*"([^"\\]+)"')


def _member_order_issues(raw: str) -> list[Issue]:
    match = _FIRST_MEMBER.match(raw)
    if match and match.group(1) != "format":
        return [Issue("$", f'the first member is "{match.group(1)}"; "format" MUST come first (spec §4)')]
    format_index = raw.find('"format"')
    version_index = raw.find('"version"')
    if format_index != -1 and version_index != -1 and version_index < format_index:
        return [Issue("$", '"version" precedes "format"; writers MUST emit format first, version second (spec §4)')]
    return []


def _schema_issues(doc: dict[str, Any]) -> list[Issue]:
    validator = Draft202012Validator(load_schema(), format_checker=FormatChecker())
    issues = []
    for error in sorted(validator.iter_errors(doc), key=lambda e: list(e.absolute_path)):
        # A failure inside anyOf/if-then surfaces as a top-level error whose message
        # dumps the whole instance; best_match descends to the telling suberror.
        chosen = best_match([error]) or error
        path = "/".join(str(part) for part in chosen.absolute_path)
        issues.append(Issue(path, chosen.message))
    return issues


def _present(obj: dict[str, Any], member: str) -> bool:
    return obj.get(member) is not None


def _semantic_issues(doc: dict[str, Any]) -> list[Issue]:
    issues: list[Issue] = []

    _check_datetime(doc, "exported_at", "", issues, require_offset=True)

    diver = doc.get("diver")
    seen_uuids: dict[str, str] = {}
    if isinstance(diver, dict):
        _claim_uuid(diver, "diver", seen_uuids, issues)
        _check_datetime(diver, "created_at", "diver", issues)

    collections = {
        name: [row for row in doc.get(name) or [] if isinstance(row, dict)]
        for name in (
            "dives",
            "trips",
            "dive_sites",
            "species",
            "gear_items",
            "gear_sets",
            "gear_service_schedules",
            "gear_service_records",
            "certifications",
        )
    }

    for name, rows in collections.items():
        for index, row in enumerate(rows):
            here = f"{name}/{index}"
            _claim_uuid(row, here, seen_uuids, issues)
            _check_datetime(row, "created_at", here, issues)

    known = {
        name: {row["uuid"] for row in rows if isinstance(row.get("uuid"), str)}
        for name, rows in collections.items()
    }

    for index, dive in enumerate(collections["dives"]):
        here = f"dives/{index}"
        _check_datetime(dive, "start_time", here, issues)
        _check_reference(dive, "trip_uuid", known["trips"], "trips", here, issues)
        _check_reference_list(dive, "dive_site_uuids", known["dive_sites"], "dive_sites", here, issues)
        _check_reference_list(dive, "gear_item_uuids", known["gear_items"], "gear_items", here, issues)
        _check_reference_list(dive, "species_uuids", known["species"], "species", here, issues)

        for cyl_index, cylinder in enumerate(dive.get("cylinders") or []):
            if not isinstance(cylinder, dict):
                continue
            cyl_path = f"{here}/cylinders/{cyl_index}"
            if _present(cylinder, "oxygen") and _present(cylinder, "helium"):
                try:
                    if cylinder["oxygen"] + cylinder["helium"] > 100:
                        issues.append(Issue(cyl_path, "oxygen + helium exceeds 100 percent"))
                except TypeError:
                    pass
            if _present(cylinder, "start_pressure") and _present(cylinder, "end_pressure"):
                try:
                    if cylinder["end_pressure"] > cylinder["start_pressure"]:
                        issues.append(Issue(cyl_path, "end_pressure exceeds start_pressure"))
                except TypeError:
                    pass

        source_file = dive.get("source_file")
        if isinstance(source_file, dict):
            _claim_uuid(source_file, f"{here}/source_file", seen_uuids, issues)

        profile = dive.get("profile")
        if isinstance(profile, dict):
            latest = 0
            for channel in ("depth", "ceiling", "temperature"):
                series = profile.get(channel)
                if isinstance(series, dict):
                    latest = max(latest, _check_series(series, f"{here}/profile/{channel}", issues))
            for series_index, series in enumerate(profile.get("pressures") or []):
                if isinstance(series, dict):
                    latest = max(
                        latest, _check_series(series, f"{here}/profile/pressures/{series_index}", issues)
                    )
            for event in profile.get("events") or []:
                if isinstance(event, dict) and isinstance(event.get("time"), (int, float)):
                    latest = max(latest, event["time"])
            duration = profile.get("duration")
            if isinstance(duration, (int, float)) and duration < latest:
                issues.append(
                    Issue(
                        f"{here}/profile/duration",
                        f"duration {duration} does not cover the latest sample or event at {latest} (spec §6.4)",
                    )
                )

    for index, trip in enumerate(collections["trips"]):
        here = f"trips/{index}"
        if _present(trip, "starts_on") and _present(trip, "ends_on"):
            try:
                if trip["ends_on"] < trip["starts_on"]:
                    issues.append(Issue(here, "ends_on precedes starts_on"))
            except TypeError:
                pass
        for loc_index, location in enumerate(trip.get("locations") or []):
            if not isinstance(location, dict):
                continue
            bbox = location.get("bbox")
            if isinstance(bbox, dict):
                try:
                    if bbox["south"] > bbox["north"]:
                        issues.append(
                            Issue(f"{here}/locations/{loc_index}/bbox", "south exceeds north")
                        )
                except (KeyError, TypeError):
                    pass

    for index, gear_set in enumerate(collections["gear_sets"]):
        _check_reference_list(
            gear_set, "gear_item_uuids", known["gear_items"], "gear_items", f"gear_sets/{index}", issues
        )

    for index, schedule in enumerate(collections["gear_service_schedules"]):
        _check_reference(
            schedule, "gear_item_uuid", known["gear_items"], "gear_items",
            f"gear_service_schedules/{index}", issues,
        )

    for index, record in enumerate(collections["gear_service_records"]):
        here = f"gear_service_records/{index}"
        _check_reference(record, "gear_item_uuid", known["gear_items"], "gear_items", here, issues)
        _check_reference(
            record, "gear_service_schedule_uuid", known["gear_service_schedules"],
            "gear_service_schedules", here, issues,
        )

    for index, certification in enumerate(collections["certifications"]):
        here = f"certifications/{index}"
        for member in ("front_file", "back_file"):
            stored = certification.get(member)
            if isinstance(stored, dict):
                _claim_uuid(stored, f"{here}/{member}", seen_uuids, issues)

    for index, item in enumerate(collections["gear_items"]):
        _check_datetime(item, "archived_at", f"gear_items/{index}", issues)

    return issues


def _claim_uuid(
    obj: dict[str, Any], path: str, seen: dict[str, str], issues: list[Issue]
) -> None:
    value = obj.get("uuid")
    if not isinstance(value, str):
        return
    if value in seen:
        issues.append(Issue(path, f"uuid {value} already used at {seen[value]}"))
    else:
        seen[value] = path


def _check_reference(
    obj: dict[str, Any],
    member: str,
    targets: set[str],
    collection: str,
    path: str,
    issues: list[Issue],
) -> None:
    value = obj.get(member)
    if isinstance(value, str) and value not in targets:
        issues.append(Issue(f"{path}/{member}", f"references {value}, not present in {collection}"))


def _check_reference_list(
    obj: dict[str, Any],
    member: str,
    targets: set[str],
    collection: str,
    path: str,
    issues: list[Issue],
) -> None:
    values = obj.get(member)
    if not isinstance(values, list):
        return
    for index, value in enumerate(values):
        if isinstance(value, str) and value not in targets:
            issues.append(
                Issue(f"{path}/{member}/{index}", f"references {value}, not present in {collection}")
            )


def _check_series(series: dict[str, Any], path: str, issues: list[Issue]) -> int:
    """Check one channel; returns the latest sample time seen (0 if none)."""
    times, values = series.get("times"), series.get("values")
    if not (isinstance(times, list) and isinstance(values, list)):
        return 0
    if len(times) != len(values):
        issues.append(Issue(path, f"times has {len(times)} samples but values has {len(values)}"))
    numbers = [value for value in times if isinstance(value, (int, float))]
    if any(later <= earlier for earlier, later in zip(numbers, numbers[1:])):
        issues.append(Issue(path, "times is not strictly increasing"))
    return max(numbers, default=0)


def _check_datetime(
    obj: dict[str, Any],
    member: str,
    path: str,
    issues: list[Issue],
    require_offset: bool = False,
) -> None:
    value = obj.get(member)
    if not isinstance(value, str):
        return
    where = f"{path}/{member}" if path else member
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        issues.append(Issue(where, f"{value!r} is not a DiveJSON date-time"))
        return
    if require_offset and parsed.tzinfo is None:
        issues.append(Issue(where, "must carry a UTC offset — it is generated, not recorded history (spec §5.2)"))
