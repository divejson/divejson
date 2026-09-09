# Changelog

Notable changes to the DiveJSON specification and its conformance suite. The specification's own
version (`major.minor`, declared in every document) is what readers and writers depend
on; the implementations that read and write it are released separately, from their own
repositories.

## Unreleased

- **A dive carries `recordings` (§6.4a), and the dive-level `profile` and `source_file`
  are gone.** A recording is one device's record of one dive — its device (§6.4b), its own
  start, its source files and its profile — and a dive has a list of them, in order, the
  first primary. Three things a logbook meets constantly had no shape before this: a diver
  wearing two computers, whose second record every reader here dropped; one recording
  exported twice, as an application's JSON beside the same device's binary, which arrived
  as two dives with two identities and half the data each; and a computer worn that
  recorded nothing, which is a fact about the dive with nowhere to sit. `recordings` is
  each of those, and §6.4b's device — brand, model, serial, firmware, name and the
  device's own dive counter — is what tells one apart from another. The serial reverses a
  sentence two mapping documents used to carry, that nothing in a logbook needs one:
  nothing did, until a logbook had to hold two records of one dive.

  **This is a breaking change and it lands inside 1.0**, which the draft's own status line
  allows — normative text, schema and fixtures may change together until the tag, and
  nothing is tagged. `$id`, `title` and `version` are untouched at `1.0`. A document
  written against an earlier draft has a `profile` on its dive, which the schema now
  rejects outright; `fixtures/invalid/dive-profile-outside-recording.divejson` is that
  shape, kept as a negative fixture so the failure is a named one. §3's beyond-schema list
  gains a rule — a recording carries at least one of `device`, `profile` and
  `source_files` — and its profile-series rule now reads per recording.

  **A gear item carries a `serial` (§6.12), and a device's maker is `brand` on both
  objects.** The two changes are one: a `computer` in the kit list and a recording's device
  are the same machine described from the logbook's two sides, and until now nothing let a
  writer say so. A serial does — equality between §6.12's and §6.4b's is what identifies
  them as one piece of hardware, where a comparison of names and makers is a guess — so
  §6.12 gains one, bounded at 1–64 rather than this section's usual 255 because a gear
  serial that could not fit a device's could never equal one. It is allowed on any gear
  type; only a computer has anything to fold with. And §6.4b's maker becomes `brand`, the
  word §6.12 already used, because two words for one fact read as two facts — the newer and
  smaller of the two collapses, rather than renaming every gear type's `brand` to a word
  that suits a wetsuit no better than it suits a reel.
  `docs/uddf-writing.md` carries the test a writer applies, and
  `docs/uddf-mapping.md` the `<serialnumber>` that feeds it. §9's personal-data bullet names
  both members now: a serial is a stable hardware identifier wherever it sits, and the kit
  list carries them for gear that never recorded a dive.

  Cylinders stay on the dive. Two devices label one gas supply however each pleases, and
  the diver keeps one list; `gas_number` remains the join key from every recording's
  pressure channels and gas switches, which is why a second computer's channels resolve
  against the dive's cylinders rather than against a list of their own.

  Every fixture carrying a profile moved with it, and `docs/converting.md` gains the table
  saying where each of the five readers takes a device from. Two readings a reader used to
  refuse are now carried, for the same reason each was refused: a device's own dive counter
  and its serial identify hardware rather than a dive, which is exactly what §6.4b is for.
  `docs/uddf-mapping.md` gains a *Generators this reader knows* table, whose one entry
  reads a `Z` from Shearwater Cloud Desktop as the local wall clock it is rather than the
  UTC it claims — a `resolved` finding, which widens that kind from a value whose scale was
  ambiguous to one whose meaning was.
- Initial draft of the DiveJSON 1.0 specification, its JSON Schema (2020-12), the
  conformance fixtures, and the `divejson validate` CLI. The draft freezes as v1.0 when
  its maintainers tag it.
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
