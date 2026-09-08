# Changelog

Notable changes to the DiveJSON specification and its conformance suite. The specification's own
version (`major.minor`, declared in every document) is what readers and writers depend
on; the implementations that read and write it are released separately, from their own
repositories.

## 1.0

- Initial draft of the DiveJSON 1.0 specification, its JSON Schema (2020-12), the
  conformance fixtures, and the `divejson validate` CLI. This release is that draft
  frozen: 1.0 is the text its maintainers tag.
- `divejson convert` reads UDDF. The format has only ever met the implementation that
  wrote it, and reading somebody else's data is the thing it exists for — so the converter
  is as much a test of the specification as a tool: it is what turns "an open interchange
  format" from a claim with one implementation behind it into one that has read a file it
  did not write. Its rules are written down separately, in `docs/uddf-mapping.md`, because
  the portable part of a converter is its rules; every fixture in the new `fixtures/uddf/`
  is paired with the document it must produce, which makes that directory a conformance
  suite for converters rather than a set of samples. The unit conversions are where a
  converter is most exposed, and no fixture here can reach them: a wrong factor produces a
  document that passes every check the corpus makes and describes a dive nobody took, so
  the tests that cover them belong to the implementation.
- Training courses (§6.17): a `courses` collection, with `course_uuid` links on dives
  and certifications, following the reference implementation shipping them — the draft
  absorbing pre-freeze additions is the policy working as intended.
- `profile.duration` spans the profile's **samples**, and an event `time` may fall past
  it (§6.4, §3 rule 3). The previous rule required `duration` to cover the latest event
  as well, which no dive computer guarantees: a marker button pressed at the surface
  after the recorder's final sample produces exactly that document, and the old rule
  forced a writer either to drop the marker or to invent a sample span the file never
  had — the second forbidden by §5.4. §6.4 now states the reader's obligation positively:
  preserve such an event where it is, and clip when plotting rather than rescaling.
- The tools moved out. The Python implementation — the validator, the UDDF converter and
  the `conform` runner — now lives in
  [divejson/divejson-py](https://github.com/divejson/divejson-py) and is released to PyPI as
  `divejson`; this repository keeps the specification, the schema, the fixtures and the
  documents, and its CI installs a pinned release to run them. What a repository holding
  both could do in one pull request, an amendment now takes two — the price of a format
  that expects ports, and of an implementation with no privileged standing over the suite
  it is measured against. `docs/converting.md` is new: the converter rules that hold
  whatever the source is, lifted out of `docs/uddf-mapping.md`, which keeps what is UDDF's.
- Three more source formats join the corpus: Subsurface's `.ssrf` save file, ANT/Garmin FIT
  and the Suunto app's JSON export, each with its pairs under `fixtures/` and its mapping
  document under `docs/`. That is the two-repository order working as designed — the reader,
  its pairs and its document land in an implementation repository first, are released, and
  are adopted here verbatim against that release. FIT is the first binary input in the tree,
  and the first committed whole rather than reduced by hand: a `.fit` cannot be hand-built
  without proving only that an encoder and a decoder agree. Five rules the new documents
  turned out to share moved into `docs/converting.md`, which is where a rule that holds for
  more than one format belongs — among them that a ceiling of zero is not a ceiling, and
  where a satellite fix belongs on a dive that has two of them.
- The corpus gains a direction. `fixtures/write/uddf/` holds the first **writer** pairs — a
  DiveJSON document, and the UDDF file a correct writer produces from it, a reader pair with
  its halves swapped — and `docs/writing.md` is new: the rules a converter follows whatever
  format it is *writing*, the counterpart to `docs/converting.md` rather than an extension
  of it, which scopes itself to reading. It opens by settling the inversion the two
  documents live with, since §1.1 defines a "writer" as software that produces DiveJSON: a
  converter is a §1.1 writer, and something turning a document back into UDDF is a §1.1
  reader. What is UDDF's own is in `docs/uddf-writing.md`, and `CONTRIBUTING.md`'s adoption
  bar now states a reader's and a writer's separately, because what the suite can hold an
  adapter to differs by direction.
- Suunto's DM5 XML is the fifth source format read, with `fixtures/suunto_xml/` and
  `docs/suunto-xml-mapping.md`. Four rules its document turned out to share with a sibling
  moved into `docs/converting.md` — a date-time matched by pattern rather than by a standard
  library's ISO parser, a time of day with no seconds, nothing a source recorded being
  quantized, and a record that is not a scuba dive being skipped and reported rather than
  arriving mislabelled by omission, DiveJSON having no member for the kind of a dive.
- Two sentences here were wrong and are corrected: `fixtures/README.md` said there were no
  writer pairs yet, and `docs/suunto-json-mapping.md` attributed first-entry-wins to a
  sample axis that merges — contradicting itself forty lines later, and mis-stating what a
  cylinder's extremes are taken over.
