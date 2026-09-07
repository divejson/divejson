# DiveJSON

<https://divejson.org> — an open interchange format for scuba dive logs. One JSON
document carries a complete logbook — dives with full sampled profiles, gas mixtures,
trips, training courses, dive sites, marine-life sightings, gear and its service
history, certifications — so a diver's data can move between applications without loss.

**Status: draft.** The 1.0 specification is feature-complete. It freezes as v1.0 when its
maintainers tag it; until then, normative text, schema, and fixtures may change together.

## Why another format

A dive log should outlive any single application, and today it doesn't. UDDF, the nominal
standard, has been frozen since 2018 — and in round-trip testing between shipping
implementations it loses trips, gear, weights, and UTC offsets, while some readers
fabricate profile points and coordinates that were never recorded. The active open-source
logbooks import each other's formats one parser at a time, and some offer no export at
all.

DiveJSON's answers, as normative rules rather than aspirations:

- **Nothing invented.** Absent means "not recorded". Writers never emit fabricated
  defaults; readers never substitute them.
- **One canonical unit system.** Metric, fixed by the spec — no per-document unit
  declarations for readers to half-implement.
- **Offsets survive.** Times travel as single offset-aware strings, and a conforming
  reader preserves the offset.
- **Self-contained.** Every cross-reference resolves inside the document.
- **Core is implemented.** Every core member has a shipping writer and reader; everything
  speculative rides the `extensions` mechanism until an implementation earns it a place.

```json
{
  "format": "divejson",
  "version": "1.0",
  "exported_at": "2026-08-28T10:15:00+00:00",
  "diver": { "uuid": "019fec35-54b9-7874-a1c7-b504a3e8e778", "name": "Sam Reef" },
  "dives": [
    {
      "uuid": "019fec36-b9ec-71c6-a03e-64f59b8b92b1",
      "started_at": "2026-04-17T11:49:23+02:00",
      "duration": 2460,
      "max_depth": 18.4,
      "cylinders": [{ "volume": 12.0, "oxygen": 32.0, "start_pressure": 200.0 }],
      "profile": { "duration": 2460, "depth": { "times": [0, 60, 120], "values": [0, 950, 1840] } }
    }
  ]
}
```

## What's in this repository

| path | what |
| --- | --- |
| [`spec/divejson.md`](spec/divejson.md) | The specification — the normative document. |
| [`schema/1.0/divejson.schema.json`](schema/1.0/divejson.schema.json) | The normative JSON Schema (draft 2020-12), one directory per minor version. |
| [`fixtures/`](fixtures/) | Conformance fixtures: valid documents, invalid ones covering each rule the schema alone cannot express, and source-format inputs paired with the documents a converter must produce from them. |
| [`docs/`](docs/) | Non-normative notes. [`converting.md`](docs/converting.md) is the converter policy every implementation follows; a mapping document beside it per source format the corpus covers — [`uddf-mapping.md`](docs/uddf-mapping.md), [`ssrf-mapping.md`](docs/ssrf-mapping.md), [`fit-mapping.md`](docs/fit-mapping.md), [`suunto-json-mapping.md`](docs/suunto-json-mapping.md). |

## Validating a document

The tooling is a separate package, [`divejson`](https://pypi.org/project/divejson/), built
from [divejson/divejson-py](https://github.com/divejson/divejson-py):

```bash
pip install divejson
divejson validate my-logbook.divejson
```

Exit status is non-zero if any file fails, with one line per violation.

## Converting a logbook

```bash
divejson convert my-logbook.uddf
```

writes `my-logbook.divejson` beside the input and reports, line by line, what the source
did not carry — no UTC offsets, a cylinder whose size nobody recorded, coordinates that
were `0.000000`. **Nothing absent is filled in**: that report is the other half of the
output, not a diagnostic, and it is what tells a diver which parts of their history their
old application never kept. The rules a converter follows whatever it is reading are in
[`docs/converting.md`](docs/converting.md); each source format's own map, its ambiguities
and what it leaves unmapped are in that format's document beside it, one per format the
corpus covers — UDDF, Subsurface `.ssrf`, ANT/Garmin FIT and the Suunto app's JSON.

## Running the conformance suite

The fixtures are a suite any implementation can be run against, and the command every
implementation provides is `conform`:

```bash
pip install divejson
divejson conform fixtures/ --strict
```

Exit status is 0 if every case passed, 1 if a case failed, and 2 if the corpus's shape is
wrong — a pair for a format the implementation does not read, say, which means cases that
never ran rather than cases that failed. CI runs exactly this against a pinned release;
[CONTRIBUTING.md](CONTRIBUTING.md) says how the pin moves.

## Media type and extension

`application/vnd.dive+json`, file extension `.divejson`. IANA registration follows the
1.0 tag. A ZIP archive convention for carrying the document together with its referenced
binaries (dive-computer files, certification scans) is described in the spec's Appendix A.

## Versioning

Documents declare `"version": "major.minor"`. Minor versions are strictly additive;
readers accept any document of a major version they implement and ignore members they do
not recognize. The full policy is §7 of the spec.

## Implementations

DiveJSON is the native export and import format of **OpenDiving**, a self-hostable dive
log and the format's reference writer; it ships with OpenDiving, and the application
repositories open at the project's public launch. The format is deliberately not tied to
it, and this repository is where that independence is kept: the spec, the schema and the
fixtures here are the complete definition, and an implementation is something that passes
them.

[divejson/divejson-py](https://github.com/divejson/divejson-py) is the first — a validator,
converters and the `conform` runner, on PyPI as
[`divejson`](https://pypi.org/project/divejson/). It has no privileged standing: it lives
in its own repository, vendors a pinned copy of this one, and is run against these fixtures
like any other. A port in another language is welcome to the same arrangement.

## Contributing

Problems, ambiguities, and proposals are GitHub issues — a real document that the spec
mishandles is the most valuable kind of report. See [CONTRIBUTING.md](CONTRIBUTING.md)
and [GOVERNANCE.md](GOVERNANCE.md) for how changes land and who decides.

## Notices

The message and field numbers in [`docs/fit-mapping.md`](docs/fit-mapping.md) were read off
the MIT-licensed global FIT profile that open decoders carry, and off the real files in
[`fixtures/fit/`](fixtures/fit) — **not** from Garmin's `Profile.xlsx`.

The FIT Protocol and FIT file format are proprietary to Garmin. This project is not
affiliated with or endorsed by Garmin, carries no part of the FIT SDK, and does not use
`garmin-fit-sdk`. Suunto, Subsurface and the other writers named in `docs/` are likewise
named to say whose output a mapping was checked against, and for nothing else.

## License

Specification prose (`spec/`): [CC BY 4.0](spec/LICENSE). Schema and fixtures (everything
else): [MIT](LICENSE).
