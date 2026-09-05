# Governance

DiveJSON is maintained by its original author. Decisions about the specification — what
enters the core data model, when a version is tagged, what a normative sentence means —
are made by the maintainer, in the open, through GitHub issues and pull requests. This is
the model TOML used through its formative years: small surface, one accountable decision
maker, everything argued in public.

## How changes happen

1. Open an issue describing the problem the change solves. For additions to the core data
   model, the bar is stated in [CONTRIBUTING.md](CONTRIBUTING.md): an implementation that
   stores the field and is prepared to read and write it.
2. Discussion happens on the issue. The maintainer decides; the reasoning stays on the
   record.
3. Accepted changes land as pull requests against the spec, the schema, and the fixtures
   together — a normative change that the schema and fixtures do not reflect is not done.
   The implementations live in repositories of their own, so a change to what validates is
   not finished until one of them has released it and this repository's CI runs against
   that release: the two orders a change can take, and which one applies, are in
   [CONTRIBUTING.md](CONTRIBUTING.md).

## Versioning

The specification carries a `major.minor` version, declared in every document. Minor
versions are strictly additive; a major version may break. The full policy is normative
text in the specification itself, and the [CHANGELOG](CHANGELOG.md) records what moved
between versions.

## If the project grows

A W3C Community Group or a foundation home becomes worth the overhead when multiple
independent implementations want a formal seat at the table. Until then, this file is the
whole constitution.
