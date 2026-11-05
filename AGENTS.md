# divejson

Read [CONTRIBUTING.md](CONTRIBUTING.md) before editing, especially "How a change lands: two
repositories, two orders". This repository owns the specification, schema, adopted mapping
documents and conformance fixtures; implementations vendor its schema/, fixtures/ and docs/.

## Ownership and merge order

An existing mapping, fixture or validation rule changes here first. The implementation pins the
spec proposal; this PR tests the matching implementation commit before merging; the implementation
then re-pins to the merged specification, merges and releases. Update the released-version pin
afterward. A new reader or writer follows the separate implementation-first order in CONTRIBUTING.md.

Check the dependency order before changing a CI pin. Requiring an implementation release while its
merge waits for this specification creates a cycle. Preserve implementation commits installed by
this repository's CI, and do not guess an unpublished version. Link companion PRs and state the
remaining merge/release steps.

## Fixture evidence and review

New mappings need shareable real-writer fixture pairs. Anonymize identifying data while preserving
the native readings, invalid sentinels, message order and relative timing needed to prove the
mapping. Retain relevant non-identifying events. Review expected-output diffs independently of the
converter that generated them, including the units and physical consistency of the readings.

Keep one-off fixture-preparation tools local unless deliberately maintained as part of the project.
Update mapping claims and the Unreleased changelog entry when behavior or coverage changes. Follow
CONTRIBUTING.md's link rules for documents that are also read in implementation repositories.

For review fixes, inspect review bodies, inline comments and discussion attachments. Reconcile each
item with the files, factual comments and PR description; removed tools and old verification results
must not remain described as current. Report unverified or blocked items explicitly.
