# Contributing

Issues and pull requests on GitHub are the whole process — there is no mailing list, no
CLA, and no meeting. [GOVERNANCE.md](GOVERNANCE.md) says who decides; this file says what
makes a contribution likely to be accepted.

## Reporting problems with the spec

The most valuable issue is a concrete document: something a real logbook produced that
the spec mishandles, a sentence two readers implemented differently, a field a real
importer needed and could not express. Attach the document (or a minimal reduction of
it) whenever you can.

## Proposing additions to the data model

The core data model contains what shipping implementations actually store — every core
field has a writer, a reader, and conformance fixtures. A field nobody stores yet is an
untestable claim, and untestable claims are how interchange formats rot.

So: propose new fields through the `extensions` mechanism first. Ship them under your
producer key, and open an issue saying so. A field graduates into core when an
implementation stores it and is prepared to keep reading and writing it — at that point
it arrives with evidence instead of speculation.

## Working on the tools

The tools live in `divejson/` and are plain Python — the validator, and `convert`, which
reads UDDF:

```bash
uv run divejson validate fixtures/valid/demo-logbook.divejson
uv run divejson convert fixtures/uddf/subsurface.uddf --output /tmp/out.divejson
```

or, without [uv](https://docs.astral.sh/uv/): `pip install -e .` and run `divejson`.

**There are tests, and they are run with pytest:**

```bash
uv run --extra dev pytest
```

or `pip install -e ".[dev]"` and then `pytest`. They cover the converter — the unit
conversions above all, where a wrong factor produces a document that validates perfectly
and is nonsense. CI runs them on the Python floor and on a current version, alongside the
fixture legs.

Changes to normative text, the JSON Schema, and the fixtures travel together: a pull
request that changes what a conforming document looks like must update all three, and
`fixtures/invalid/` must keep one file per rule the schema alone cannot express.

A change to the converter travels with `fixtures/uddf/` the same way. Each input there is
paired with the document it must produce, so a mapping change shows up as a failing pair.
Regenerate the expected side, and read the diff before committing it — the point of the
pair is that a human agreed with the new answer:

```bash
uv run divejson convert fixtures/uddf/<name>.uddf --force \
  --exported-at "$(grep -m1 exported_at fixtures/uddf/<name>.divejson | cut -d'"' -f4)"
```

Both flags matter. Without `--force` the command refuses to replace a file that exists,
which is the right default everywhere except here. And `exported_at` is one of the two
members a converted document asserts about its own run rather than about the source, so
left to default it moves every time — reusing the value already in the file you are
replacing keeps the moving lines to the ones your change actually moved.

The other such member is `generator`, which carries this package's version and so moves
when that does. Both are excluded from the pair comparison for the same reason, so a
release needs no regeneration; regenerate the corpus when the *mapping* changes.
[`fixtures/README.md`](fixtures/README.md) says what is compared.

The rules those expectations follow are written down in
[`docs/uddf-mapping.md`](docs/uddf-mapping.md) — that document is the portable part of the
converter, and it is not optional to update.

## Pull request titles

Use a semantic **PR title** — `<type>[(scope)][!]: <description>`, where type is one of
`feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `ci`, `build`, `revert`.
Pull requests are squash-merged with the title as the commit subject, so it is the only
part of a branch that outlives the branch.

`.github/workflows/pr-title.yml` checks the format and re-runs when a title is edited —
a failing check is fixed by correcting the title, with nothing to push.

## Licensing of contributions

Specification prose is CC BY 4.0; schema, fixtures, and tools are MIT (see
[README.md](README.md#license)). By contributing you license your contribution under the
license of the part you are contributing to.
