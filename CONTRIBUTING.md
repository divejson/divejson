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

## Running the conformance suite

This repository is the suite: the specification, the schema, and the fixtures an
implementation is measured against. It carries no implementation of its own. Install one
and ask it to run the corpus:

```bash
pip install divejson
divejson conform fixtures/ --strict
```

`conform` is the command every implementation provides, so a port in another language runs
the same line. Exit status is 0 if every case passed, 1 if a case failed, and 2 if the
corpus's shape is wrong — a pair directory for a format the implementation does not read,
a pair missing one of its halves, an empty corpus — all of which mean cases that never ran
rather than cases that failed. `--strict` adds the mirror of that: a format the
implementation reads and the corpus has no pairs for is an error too, so the suite cannot
quietly stop covering a reader.

CI pins the release it installs, in `DIVEJSON_VERSION` at the top of
`.github/workflows/ci.yml`. Moving to a newer release is a one-line pull request of its
own, and it is meant to be a deliberate act: an unpinned install would let a release
nobody here has looked at decide whether the corpus passes.

A released implementation carries its own copy of `schema/` and resolves that one; it
never reads the corpus directory it is pointed at. So CI asserts that the two are byte-equal
before it runs the corpus, and that assertion is what makes the run a run against the schema
in this tree. It is also what makes a schema change here **red on the pinned release**
rather than quietly unchecked, which is the first of the two orders below.

Changes to normative text, the JSON Schema, and the fixtures travel together: a pull
request that changes what a conforming document looks like must update all three, and
`fixtures/invalid/` must keep one file per rule the schema alone cannot express.

## How a change lands: two repositories, two orders

The implementations live in repositories of their own —
[divejson/divejson-py](https://github.com/divejson/divejson-py) is the first. Each vendors
a copy of this repository's `schema/`, `fixtures/` and `docs/` and pins the commit it was
taken from, and its CI asserts that every file this repository owns is byte-identical over
there. **An implementation never edits a file this repository owns.** It may carry files
this repository does not have yet — that is how a new reader lands self-contained, with the
expected documents it produces and the mapping document that explains them.

So a change goes one of two ways, and which one it is depends on whether it touches a file
that already exists here.

**A change to what validates** — the specification, the schema, a rule the fixtures encode,
or anything in a file this repository already owns, an adopted mapping document and an
adopted pair included — starts **here**. Its pull request is red against the pinned release
and says what is missing. The implementation's pull request then pins this one's head,
which passes its byte check and fails only its ancestor check; this pull request moves
`DIVEJSON_VERSION`, or the pin, at the implementation's head and goes green; it merges;
the implementation re-pins to the merged commit, merges, and is released; a one-line chore
here moves `DIVEJSON_VERSION` to that release.

**A new reader** starts **there**: self-contained and green in the implementation
repository, with its pairs and its mapping document, then a release, then a pull request
here adopting the pairs and the document verbatim and moving the pin. If the new document
turns out to state a rule that holds for every format, that pull request is where it moves
into [`docs/converting.md`](docs/converting.md); the implementation picks the edited
documents back up at its next pin bump.

Regenerating an expected document is the implementation's business — its recipe is in
`divejson-py`'s `CONTRIBUTING.md`, and the point of it is the same in either order: read
the diff before committing it, because what makes a pair a conformance case is that a human
agreed with the new answer.

## Adding an adapter

An adapter — a reader for a new source format, in any implementation repository — is
adopted into this corpus when it arrives with:

- a **mapping document** in `docs/`, carrying what is that format's and nothing that
  [`docs/converting.md`](docs/converting.md) already says;
- **at least one pair per writer it claims to read**, because a format is a family of
  dialects and a claim about a writer is only checked by a file that writer produced;
- **its report's kinds documented** — what it reports as absent, as inferred, and as
  dropped.

The maintainer decides, as for everything else. This is a different bar from the one for
new core fields above: that one is about what the format models, this one is about what the
suite can hold you to.

## Pull request titles

Use a semantic **PR title** — `<type>[(scope)][!]: <description>`, where type is one of
`feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `ci`, `build`, `revert`.
Pull requests are squash-merged with the title as the commit subject, so it is the only
part of a branch that outlives the branch.

`.github/workflows/pr-title.yml` checks the format and re-runs when a title is edited —
a failing check is fixed by correcting the title, with nothing to push.

## Licensing of contributions

Specification prose is CC BY 4.0; schema and fixtures are MIT (see
[README.md](README.md#license)). By contributing you license your contribution under the
license of the part you are contributing to.
