# DiveJSON

<https://divejson.org> — an open interchange format for scuba dive logs. One JSON
document carries a complete logbook — dives with full sampled profiles, gas mixtures,
trips, training courses, dive sites, marine-life sightings, gear and its service
history, certifications — so a diver's data can move between applications without loss.

**Status: draft.** The 1.0 specification is feature-complete and in round-trip testing
against its reference implementation; it freezes as v1.0 when that passes. Until the tag,
normative text, schema, and fixtures may change together.

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
| [`fixtures/`](fixtures/) | Conformance fixtures: valid documents, and invalid ones covering each rule the schema alone cannot express. |
| [`divejson/`](divejson/) | The reference validator — schema pass plus the beyond-schema checks. |

## Validating a document

With [uv](https://docs.astral.sh/uv/), from a checkout:

```bash
uv run divejson validate my-logbook.divejson
```

or install it: `pip install git+https://github.com/divejson/divejson` and run
`divejson validate <file>`. Exit status is non-zero if any file fails, with one line per
violation.

## Media type and extension

`application/vnd.dive+json`, file extension `.divejson`. IANA registration follows the
1.0 tag. A ZIP archive convention for carrying the document together with its referenced
binaries (dive-computer files, certification scans) is described in the spec's Appendix A.

## Versioning

Documents declare `"version": "major.minor"`. Minor versions are strictly additive;
readers accept any document of a major version they implement and ignore members they do
not recognize. The full policy is §7 of the spec.

## Reference implementation

DiveJSON is the native export and import format of **OpenDiving**, a self-hostable dive
log; it ships with OpenDiving, and the application repositories open at the project's
public launch. The format is deliberately not tied to it: the spec, schema, fixtures, and
validator in this repository are the complete definition.

## Contributing

Problems, ambiguities, and proposals are GitHub issues — a real document that the spec
mishandles is the most valuable kind of report. See [CONTRIBUTING.md](CONTRIBUTING.md)
and [GOVERNANCE.md](GOVERNANCE.md) for how changes land and who decides.

## License

Specification prose (`spec/`): [CC BY 4.0](spec/LICENSE). Schema, fixtures, and tools
(everything else): [MIT](LICENSE).
