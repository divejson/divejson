# Changelog

Notable changes to the DiveJSON specification and its tools. The specification's own
version (`major.minor`, declared in every document) is what readers and writers depend
on; tool releases are versioned separately in `pyproject.toml`.

## Unreleased

- Initial draft of the DiveJSON 1.0 specification, its JSON Schema (2020-12), the
  conformance fixtures, and the `divejson validate` CLI. The draft freezes as v1.0 only
  after the reference implementation's export/import round-trip passes against it.
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
