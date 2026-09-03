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

The validator lives in `divejson/` and is plain Python:

```bash
uv run divejson validate fixtures/valid/demo-logbook.divejson
```

or, without [uv](https://docs.astral.sh/uv/): `pip install -e .` and run `divejson`.

Changes to normative text, the JSON Schema, and the fixtures travel together: a pull
request that changes what a conforming document looks like must update all three, and
`fixtures/invalid/` must keep one file per rule the schema alone cannot express.

## Licensing of contributions

Specification prose is CC BY 4.0; schema, fixtures, and tools are MIT (see
[README.md](README.md#license)). By contributing you license your contribution under the
license of the part you are contributing to.
