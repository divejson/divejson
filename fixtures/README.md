# Conformance fixtures

`divejson validate` must pass every document in `valid/` and reject every document in
`invalid/`. CI enforces exactly that, so a change to the spec or schema that alters what
conforms shows up here as a failing fixture — update the three together
([CONTRIBUTING.md](../CONTRIBUTING.md)).

## valid/

| file | what it covers |
| --- | --- |
| `minimal.divejson` | The smallest conforming document: `format`, `version`, `exported_at` — no diver (a source that records nothing about its owner omits the member), no collections (absent ≡ empty). |
| `demo-logbook.divejson` | A real export of the reference implementation's demo account (all names are seeded demo data; pulled 2026-09-02, courses-era writer): 8 dives, one with a full sampled profile from a dive computer, sites, trips, an empty `courses` collection, gear with a service history, certifications, and producer extensions carrying application-specific values. Regenerate from a fresh export when the writer changes. |
| `technical-dive.divejson` | Hand-built coverage of what the demo corpus lacks: trimix, a sidemount pair (two cylinders, one blend, `usage: "parallel"`), staged deco cylinders, gas-switch events, a ceiling channel with a gap, per-cylinder pressure channels, a `+12:45` UTC offset **and** an offset-less local `started_at` (§5.2's third state), a dive with no recorded duration, a common-name-only species, an antimeridian-crossing bounding box, an `agency: "other"` certification with `front_file`/`back_file`, a dive-count service interval, two courses — a completed `"other"`-agency course linked from a dive and its certification, and an unreferenced `"planned"` one with no dates — a lowercase-`z`, one-digit-fraction `created_at` (both spellings the grammar allows and naive parsers reject), and an event 85 s **past** `profile.duration` — the surface-marker case §6.4 blesses, which no other fixture covers and which the pre-2026-09-04 validator rejected. |

## invalid/

One defect per file. Every rule the schema alone cannot express (spec §3) has a fixture
here; several schema-level defects are included so the validator's schema pass and the
format's structural guarantees (Position objects, the null ban) are exercised too.

| file | defect | spec |
| --- | --- | --- |
| `bad-version.divejson` | `version` is `"0.9"` | §4, §7 |
| `missing-format.divejson` | no `format` member | §4 |
| `version-before-format.divejson` | `version` serialized before `format` | §4 |
| `version-not-second.divejson` | `format` first but another member before `version` | §4 |
| `null-member.divejson` | a member carried as `null` | §5.4 |
| `undefined-member.divejson` | an undefined member outside `extensions` | §5.5 |
| `duplicate-json-member.divejson` | the same JSON member name twice in one object | §9 |
| `duplicate-uuid.divejson` | two records share a uuid | §5.3 |
| `dangling-reference.divejson` | a `site_uuids` entry resolves to nothing | §5.3 |
| `naive-exported-at.divejson` | `exported_at` without a UTC offset | §5.2 |
| `trailing-newline-datetime.divejson` | a date-time with a trailing newline inside the string | §5.2 |
| `position-incomplete.divejson` | a Position missing `longitude` | §6 |
| `oxygen-helium-sum.divejson` | `oxygen + helium > 100` on a cylinder | §6.3 |
| `pressure-order.divejson` | `end_pressure > start_pressure` on a cylinder | §6.3 |
| `avg-depth-exceeds-max.divejson` | `avg_depth > max_depth` on a dive | §6.2 |
| `profile-duration-short.divejson` | `profile.duration` below the latest sample | §6.4 |
| `channel-length-mismatch.divejson` | a series' `times` and `values` differ in length | §6.5 |
| `non-increasing-samples.divejson` | a series' `times` is not strictly increasing | §6.5 |
| `event-other-without-label.divejson` | an `"other"` event with no label | §6.6 |
| `trip-dates-reversed.divejson` | `ends_on` before `starts_on` on a trip | §6.8 |
| `course-dates-reversed.divejson` | `ends_on` before `starts_on` on a course | §6.17 |
| `bbox-missing-corner.divejson` | a Bounding Box missing one corner | §6.9 |
| `bbox-south-exceeds-north.divejson` | `south > north` in a Bounding Box | §6.9 |
| `bbox-without-position.divejson` | a `bbox` on a location with no `position` | §6.9 |
| `species-no-identity.divejson` | a species with no AphiaID and no name at all | §6.11 |
| `agency-other-missing.divejson` | `agency: "other"` without `agency_other` | §6.16 |
