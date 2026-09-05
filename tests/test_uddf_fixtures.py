"""Every UDDF fixture converts to the `.divejson` beside it.

The pairs in `fixtures/uddf/` are a conformance suite for *converters*, the way
`fixtures/valid` and `fixtures/invalid` are one for validators: an input, and the document
a correct reader produces from it. The Python converter in this repository is the first to
be run against them and deliberately not the last, so a port in another language can take
the same directory and expect the same answers.

Two members are excluded from the comparison, and only two — `exported_at` and
`generator`. Both are facts about the *run* rather than about the input: the first is the
moment of conversion and the second is whatever software did it, which for a port is not
this one. Everything else is compared, `extensions` included: the provenance block under
the `divejson` producer key records the source's own version and generator, which are
properties of the input like any other.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest
from helpers import FIXTURES

from divejson.uddf import convert_uddf_file
from divejson.validate import validate_document

# What the expected documents were generated with. Any instant does: the member it lands
# in is one of the two the comparison ignores, and pinning it only keeps the files from
# churning every time they are regenerated.
EXPORTED_AT = datetime(2026, 9, 5, tzinfo=timezone.utc)

IGNORED = ("exported_at", "generator")

UDDF_FIXTURES = sorted((FIXTURES / "uddf").glob("*.uddf"))


def compared(document: dict) -> dict:
    return {member: value for member, value in document.items() if member not in IGNORED}


def test_there_are_fixtures_to_compare() -> None:
    """A glob that silently matches nothing is how a suite stops testing anything."""
    assert len(UDDF_FIXTURES) >= 5


@pytest.mark.parametrize("uddf", UDDF_FIXTURES, ids=lambda path: path.stem)
def test_fixture_converts_to_its_expected_document(uddf) -> None:
    expected_path = uddf.with_suffix(".divejson")
    assert expected_path.is_file(), f"{uddf.name} has no expected output beside it"
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    produced = convert_uddf_file(uddf, exported_at=EXPORTED_AT).document
    assert compared(produced) == compared(expected)


@pytest.mark.parametrize("uddf", UDDF_FIXTURES, ids=lambda path: path.stem)
def test_expected_document_is_conforming(uddf) -> None:
    """Checked here as well as in CI, so a hand-edited expectation fails at the same desk."""
    expected = json.loads(uddf.with_suffix(".divejson").read_text(encoding="utf-8"))
    assert validate_document(expected) == []


def test_every_expected_document_has_an_input() -> None:
    """The other direction: a `.divejson` with no `.uddf` beside it is a leftover."""
    orphans = [
        path.name
        for path in sorted((FIXTURES / "uddf").glob("*.divejson"))
        if not path.with_suffix(".uddf").is_file()
    ]
    assert orphans == []


def test_the_mix_only_cylinder_keeps_its_gas_and_loses_only_its_size() -> None:
    """The shape §6.3 blesses and no file on disk carried until this fixture.

    A cylinder converted from a mix-only source is "a cylinder with its vessel members
    absent". The gas, both pressures and a real drop between them are all present, so the
    size is the *only* input a gas-consumption figure lacks — which is what makes this
    fixture able to reach a reader's size-specific refusal rather than an earlier one.
    """
    dives = convert_uddf_file(FIXTURES / "uddf" / "mix-only-cylinder.uddf").document["dives"]
    cylinder = dives[0]["cylinders"][0]
    assert "volume" not in cylinder
    assert cylinder["oxygen"] == 32.0
    assert cylinder["start_pressure"] > cylinder["end_pressure"]
    assert "avg_depth" in dives[0]
    # The second dive has no `<tankdata>` at all, which is what APD DiveSight exports.
    assert "cylinders" not in dives[1]


def test_the_reference_implementations_own_identities_survive_the_round_trip() -> None:
    """`dive-<uuid>` ids come back as those uuids, rather than as fresh ones.

    §5.3 asks that identifiers be stable across exports of the same data. A writer holding
    real uuids has to prefix them to satisfy `xs:ID`, and recovering them is what keeps a
    logbook that went out through UDDF recognisable when it comes back.
    """
    document = convert_uddf_file(FIXTURES / "uddf" / "opendiving.uddf").document
    assert document["dives"][0]["uuid"] == "0198a6f0-5555-7001-8000-000000000001"
    assert document["sites"][0]["uuid"] == "0198a6f0-3333-7001-8000-000000000001"
    assert document["trips"][0]["uuid"] == "0198a6f0-4444-7001-8000-000000000001"
    assert document["dives"][0]["site_uuids"] == [document["sites"][0]["uuid"]]
    assert document["dives"][0]["trip_uuid"] == document["trips"][0]["uuid"]
