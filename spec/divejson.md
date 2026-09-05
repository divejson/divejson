# DiveJSON 1.0 — draft

An open interchange format for scuba dive logs.

**Status of this document:** working draft. It freezes as version 1.0 when its maintainers
tag it; until then, normative text, the JSON Schema, and the fixtures may change together
without a version bump. The canonical home of this specification is <https://divejson.org>; the repository
of record is <https://github.com/divejson/divejson>. This document is licensed
[CC BY 4.0](LICENSE).

## 1. Introduction

A dive log is a diver's property, and it outlives any single application. DiveJSON is a
JSON document format for moving a complete logbook between applications without loss:
dives with full sampled profiles, gas mixtures, trips, training courses, dive sites,
marine-life sightings, gear and its service history, and certifications.

The format exists because the field lacks a working interchange format. UDDF, the nominal
incumbent, is XML, frozen since 2018, and — measurably, in round-trip testing between
shipping implementations — loses trips, gear, weights, and UTC offsets, while some of its
readers fabricate values that were never recorded. DiveJSON's design answers those
failures directly:

- **Nothing invented.** A value that was not recorded is absent, and a reader never
  fabricates one (§5.4).
- **One canonical unit system.** Every measurement is metric with the units fixed by this
  specification; there are no per-document unit declarations for readers to half-implement
  (§5.1).
- **Instants keep their offsets.** Times travel as single strings that carry their UTC
  offset whenever the source recorded one — and never a fabricated one when it didn't
  (§5.2).
- **Self-contained documents.** Every cross-reference resolves inside the document (§5.3).
- **Core is implemented, not aspirational.** Every member defined here has a shipping
  writer and reader in the reference implementation, and conformance fixtures. Everything
  else rides the extension mechanism until an implementation earns it a place (§5.5).

### 1.1 Conformance classes

This specification defines three conformance classes:

- A **DiveJSON document**: a JSON document satisfying the requirements of this
  specification.
- A **writer**: software that produces DiveJSON documents.
- A **reader**: software that consumes DiveJSON documents.

## 2. Notational conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD
NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in BCP 14 [RFC 2119] [RFC 8174] when, and only when, they appear
in all capitals, as shown here.

A DiveJSON document is a JSON document as defined by [RFC 8259], encoded in UTF-8. The
terms "object", "member", "array", "number", "string", "boolean", and "null" are used as
defined there. "Member" refers to a name/value pair of a JSON object; this document also
uses "field" informally with the same meaning.

The named object types defined in §4 and §6 (Generator, Diver, Dive, Cylinder, Trip, …)
are collectively the **spec-defined objects**.

## 3. Conformance and the JSON Schema

The normative statement of the format is this document. The JSON Schema at
[`schema/1.0/divejson.schema.json`](../schema/1.0/divejson.schema.json) (JSON Schema
draft 2020-12, canonically `https://divejson.org/schema/1.0/divejson.schema.json`) is a
normative companion: a document that fails the schema for its declared
minor version is not a conforming DiveJSON document.

The schema cannot express every requirement. The requirements listed below are normative
but live outside the schema; the reference validator (`divejson validate`) checks both
the schema and this list:

1. Identifier uniqueness and referential closure (§5.3).
2. Cross-member arithmetic: `oxygen + helium ≤ 100` and `end_pressure ≤ start_pressure`
   on a cylinder (§6.3); `avg_depth ≤ max_depth` on a dive (§6.2); `ends_on ≥ starts_on`
   on a trip (§6.8) and on a course (§6.17); `south ≤ north` on a bounding box (§6.9).
3. Profile series integrity: equal `times`/`values` lengths and strictly increasing
   `times` (§6.5), and `profile.duration` covering the latest sample (§6.4).
4. The offset requirement on `exported_at` (§5.2) — every other date-time may be a
   local time, and the schema's `format` annotations are not required to be enforced by
   validators.
5. The member-order rule for `format` and `version` (§4) — a property of the document's
   text, which the reference validator checks on the parsed member order (JSON parsing
   preserves it).

Requirements addressed to writer and reader *behaviour* — nothing invented (§5.4),
unknown-member and unknown-value tolerance (§5.6), offset preservation (§5.2) — are not
checkable against a document at all and bind implementations directly.

The schema for minor version `1.n` describes exactly the members that version defines,
and rejects undefined members outside `extensions` objects. Validating a document against
the schema of a *different* minor version is not conformance-meaningful; the tolerance
rules readers follow across minor versions are §5.6's, not the schema's.

## 4. Document structure

A DiveJSON document is a single JSON object:

| member | type | presence | meaning |
| --- | --- | --- | --- |
| `format` | string | REQUIRED | The literal `"divejson"`. Writers MUST emit it as the first member, so readers can dispatch before parsing further. |
| `version` | string | REQUIRED | The spec version the document conforms to, as `"major.minor"` — for this specification, `"1.0"`. Writers MUST emit it second. |
| `exported_at` | string, date-time (§5.2) | REQUIRED | When the document was produced. Always offset-aware: the writer is producing this value now and knows its own offset. |
| `generator` | Generator object | RECOMMENDED | What produced the document. |
| `diver` | Diver object (§6.1) | RECOMMENDED | Whose logbook this is. Omitted only when the source records nothing about its owner (§6.1). |
| `dives` | array of Dive (§6.2) | OPTIONAL | |
| `trips` | array of Trip (§6.8) | OPTIONAL | |
| `courses` | array of Course (§6.17) | OPTIONAL | |
| `sites` | array of Dive Site (§6.10) | OPTIONAL | |
| `species` | array of Species (§6.11) | OPTIONAL | |
| `gear` | array of Gear Item (§6.12) | OPTIONAL | |
| `gear_sets` | array of Gear Set (§6.13) | OPTIONAL | |
| `gear_service_schedules` | array of Service Schedule (§6.14) | OPTIONAL | |
| `gear_service_records` | array of Service Record (§6.15) | OPTIONAL | |
| `certifications` | array of Certification (§6.16) | OPTIONAL | |
| `extensions` | object (§5.5) | OPTIONAL | |

An absent collection is equivalent to an empty one. Writers SHOULD order `dives`
chronologically; readers MUST NOT depend on collection ordering.

The **Generator** object has two members: `name` (string, REQUIRED) and `version`
(string, OPTIONAL — omitted when unknown) — the producing software and its release,
free-form.

## 5. Common rules

### 5.1 Units and scales

Every measurement in a DiveJSON document is metric, in the units fixed by this table.
There are no per-document or per-member unit declarations, and member names carry no unit
suffixes. A writer whose internal storage is imperial MUST convert; how an application
*displays* values is its own business and travels nowhere in the document.

| quantity | unit | JSON type |
| --- | --- | --- |
| depth, altitude, visibility, distance | meters | number |
| temperature | degrees Celsius | number |
| pressure (cylinder, surface) | bar | number |
| weight | kilograms | number |
| volume (cylinder water capacity) | liters | number |
| gas fractions (`oxygen`, `helium`) | percent of the mix | number |
| duration, elapsed time | seconds | integer |
| CNS | percent | number |
| OTU | OTU (dimensionless) | number |
| coordinates | decimal degrees, WGS 84 | number |

**Profile channels are integer-scaled** (§6.5): depth and ceiling samples are
**centimeters**, temperature samples are **tenths of a degree Celsius**, and pressure
samples are **tenths of a bar**. The scales are part of the format, chosen so that
sampled channels round-trip without floating-point noise while exceeding the precision of
real dive computers. Values everywhere *outside* profile channels are plain numbers in
the base units above.

### 5.2 Dates and times

A **date-time** value is a single [RFC 3339] date-time string, e.g.
`"2026-04-17T11:49:23+02:00"` — the local wall clock together with its UTC offset,
carrying both the instant and the wall clock, which are both logbook data. `Z` and
`+00:00` are conforming and equivalent. Fractional seconds are OPTIONAL.

**When the source did not record an offset, the offset is omitted**, giving a *local
date-time*: the RFC 3339 grammar minus the offset part, e.g. `"2026-04-17T11:49:23"`. A
local date-time means the wall clock was recorded and the instant is unknown. It exists
because real migration sources — UDDF pipelines above all — routinely destroy offsets,
and a converter meeting such a source has no honest third option: fabricating an offset
violates §5.4 and poisons the record undetectably, and dropping the dive is the data
loss this format exists to end. Readers MUST NOT assume an offset for a local date-time,
MUST NOT convert it to any zone, and MUST preserve it as a wall clock.

**Where an offset exists, it travels, and a conforming reader preserves it.** This is
stated explicitly because it is the failure every tested UDDF consumer produced:
converting to UTC or to the reader's zone keeps the instant but destroys the wall clock,
or the reverse. A reader whose storage cannot hold an offset MUST store it separately
rather than discard it.

The one member that MUST always carry an offset is the envelope's `exported_at`: it is
generated at write time by a writer that knows its own offset, not recorded history.

A **date** value is an RFC 3339 full-date string, `"YYYY-MM-DD"`, with no time and no
offset. Dates in a logbook (trip dates, service dates, certification dates) are calendar
facts, not instants.

**Member naming follows the value kind**: members holding date-times end `_at`
(`created_at`, `archived_at`, `exported_at`, a dive's `started_at`); members holding
dates end `_on` (`starts_on`, `serviced_on`, `certified_on`). There are no exceptions.

### 5.3 Identity and cross-references

Every record in a top-level collection carries a `uuid` member: an [RFC 9562] UUID in its
canonical lowercase text form. The producer assigns it; any version is acceptable.
Stored-file records (§6.7) and the diver (§6.1) carry uuids too.

- Every `uuid` in the document MUST be unique — one identifier space across all
  collections, stored-file records and the diver included.
- Cross-references between records are by `uuid`, through the members named `*_uuid` and
  `*_uuids`. Every referenced uuid MUST resolve to a record in the corresponding
  collection of the **same document** — a DiveJSON document is self-contained. A writer
  that cannot include a referenced record MUST omit the reference, never emit a dangling
  one.
- A reference-list member (`site_uuids`, `gear_uuids`, `species_uuids`,
  `gear_uuids` on a gear set) MUST NOT contain the same uuid twice.
- Reference-list order is meaningful and writers MUST preserve the source order: a dive's
  `site_uuids` leads with the primary site, and the rest of that list — like
  `species_uuids` and `gear_uuids` on a dive and on a gear set — is the diver's own
  order, whatever it means to them.

uuids identify records *within* a logbook and, for the same diver's data, across
exports. They are not portable identities for shared realities: the same physical dive
site or animal species in two different logbooks will carry two unrelated uuids. Where a
record has an external identity that does mean the same thing everywhere — a species'
WoRMS AphiaID (§6.11) — that identity, not the uuid, is the interchange key.

Embedded objects (cylinders, profile, trip locations, positions) have no
independent identity; stored-file records (§6.7) do carry a `uuid` because files are
addressable objects in the source logbook.

### 5.4 Absent members, null, and "nothing invented"

A member whose value was never recorded is **omitted**. There is exactly one spelling of
"not recorded", and it is absence: **writers MUST NOT emit `null`**, and the schema
rejects it. (A reader that meets a stray `null` anyway SHOULD treat the member as absent
rather than fail — but the document that carried it is not conforming.) An empty string
is a recorded value (an empty note), not an absence, and an absent collection is
equivalent to an empty one.

**Writers MUST NOT emit a fabricated value for something the source did not record.**
There are no default values in this format: no implied "air" for a missing gas mix, no
`0` for a missing depth, no `(0, 0)` for a missing position, no synthesized profile
samples. This rule is normative and load-bearing — fabricated defaults are the documented
failure mode of existing dive-log interchange, where tested consumers have invented
six-point dive profiles and zero-zero coordinates for data that was simply absent.

Symmetrically, **readers MUST NOT substitute defaults for absent values** when importing;
an absent value imports as absent. A reader MAY *derive* values it clearly labels as
derived (an average depth computed from a profile, say) but MUST NOT present a derivation
as recorded data.

The REQUIRED members of each object are the minimal set without which the record cannot
be interpreted at all. They are deliberately fewer than what the reference implementation
itself always writes: a converter from a poorer format MUST be able to omit what its
source never had rather than invent it.

### 5.5 Extensions

Every spec-defined object MAY carry an `extensions` member: an object whose member names
are **producer keys** and whose values are any JSON value (an object is RECOMMENDED).

```json
"extensions": {
  "opendiving": { "units": "metric" },
  "com.example.divekit": { "mood": "great" }
}
```

- A producer key MUST match `^[a-z0-9][a-z0-9._-]*$`. Use a reverse-DNS name for a domain
  you control (`com.example.divekit`) or an established product name (`opendiving`, the
  reference implementation's key). Choose one key and keep it stable.
- A writer MUST NOT emit members this specification does not define anywhere *except*
  inside `extensions`. This is what keeps the core vocabulary meaningful: a member
  outside `extensions` is either spec-defined or a conformance error, never a guess.
- A reader MUST ignore extension entries it does not recognize, and MUST NOT fail on
  any well-formed `extensions` content.
- A reader that re-emits a document SHOULD preserve extension entries it did not
  understand. A reader importing into its own storage is not expected to preserve them.

Extensions are the path into the core: a member that proves itself under a producer key —
an implementation stores it and is prepared to keep reading and writing it — is a
candidate for the next minor version.

### 5.6 Unknown members and forward compatibility

Minor versions of this specification are strictly additive (§7). A reader implementing
version `1.m` reading a document declaring `1.n` where `n > m` will therefore encounter
members — and, in members with closed value sets, values — it does not know. **Readers
MUST ignore members they do not recognize** — process the document as if the unknown
members were absent — and MUST NOT reject a document for containing them. **In a member
defined with a closed value set, a reader encountering a value it does not recognize
MUST treat that member as absent** (not recorded); this is what makes §7's promise that
minor versions may add enum values actually hold for old readers, and it is why §7
forbids growing the vocabulary of a REQUIRED member.

This tolerance rule is addressed to readers. It does not license writers to emit
undefined members: writer conformance is §5.5's rule, checked strictly by the schema for
the version the document declares.

### 5.7 Derived members

A few members are **derived**: the source application computed them from other records
rather than recording them as facts (they are marked "derived" where they are defined —
`dive_count` on a gear item; `last_service_on`, `next_due_on`, and
`next_due_at_dive_count` on a service schedule). Writers MUST emit values that are true
in the source logbook at export time. A reader importing into its own store SHOULD
recompute derived members from what it imported rather than trust them, since its own
view of the underlying records may differ.

Point-in-time *snapshots* (`dive_count_at_start` on a schedule, `dive_count_at_service`
on a service record) are not derived: they are historical facts with no recomputation
procedure, and readers restoring a logbook import them as recorded.

`created_at` members record when each record entered the source logbook. They are logbook
history: a reader restoring or migrating a logbook SHOULD preserve them.

## 6. Object definitions

Presence column: **R** = REQUIRED, **O** = OPTIONAL — omitted when not recorded, never
null (§5.4). Types are JSON types; `date-time` and `date` are strings per §5.2, `uuid`
per §5.3. String length limits are counted in Unicode code points. Every object below
MAY additionally carry `extensions` (§5.5); the tables do not repeat it.

A **Position** is an object `{"latitude": …, "longitude": …}`, both members REQUIRED,
WGS 84 decimal degrees (latitude −90 to 90, longitude −180 to 180). Grouping the pair
into one object is deliberate: half a coordinate is unrepresentable, which is §5.4
enforced by shape rather than by rule.

### 6.1 Diver

The owner of the logbook. The member is RECOMMENDED: a writer that knows anything about
the owner emits it, and a converter whose source records nothing about an owner omits
it entirely — an ownerless logbook is still a logbook, and minting identity for one
would be §5.4's fabrication applied to people. In particular, a converter MUST NOT mint
a fresh `uuid` per export: §5.3 presents uuids as stable for the same diver's data
across exports, and a per-export uuid is fake continuity that misleads deduplicating
importers.

| member | type | presence | constraints / meaning |
| --- | --- | --- | --- |
| `uuid` | uuid | O | The diver's identity within this document (§5.3) — stable across the same source's exports. |
| `name` | string | O | Display name. |
| `username` | string | O | The diver's handle in the source application. |
| `email` | string | O | Contact address. |
| `created_at` | date-time | O | When the account or logbook was created. |

Application preferences (display units, notification settings) are not logbook data and
have no core members; the reference implementation carries its own under its producer
key, e.g. `"extensions": {"opendiving": {"units": "metric", "gear_service_emails":
true}}`. Readers importing a logbook into an existing account MUST NOT let any diver
member overwrite the destination account's own identity or settings.

### 6.2 Dive

| member | type | presence | constraints / meaning |
| --- | --- | --- | --- |
| `uuid` | uuid | R | |
| `dive_number` | integer | O | The diver's own numbering. Unbounded; duplicates are legal (renumbering histories are messy and this format records, not adjudicates). |
| `started_at` | date-time | R | Local wall clock, with its UTC offset when the source recorded one (§5.2). |
| `duration` | integer | O | Seconds; > 0. The dive's own duration as logged, which MAY differ from the profile's span. |
| `notes` | string | O | ≤ 10000. |
| `max_depth` | number | O | Meters; > 0. |
| `avg_depth` | number | O | Meters; > 0, and MUST be ≤ `max_depth` when both are present. |
| `bottom_temperature` | number | O | °C; unbounded (ice divers and volcanic vents exist). |
| `visibility` | number | O | Meters; ≥ 0. A number, not an integer — half-meter visibility is a real low-vis fact. |
| `weight` | number | O | Kilograms of ballast; ≥ 0. `0` is a recorded "no lead", distinct from absent. |
| `water_type` | string | O | One of `"salt"`, `"fresh"`, `"brackish"`, `"en13319"` (the EN 13319 calibration convention dive computers use). No "other": an unlistable water type is simply not recorded. |
| `altitude` | integer | O | Meters above sea level of the site at dive time; −450 to 6500 (Dead Sea to the highest reported altitude dives). |
| `cns_start` | number | O | CNS %, ≥ 0, at dive start. No upper bound — real computers report over 100. |
| `cns_end` | number | O | CNS %, ≥ 0, at dive end. |
| `otu_start` | number | O | OTU accumulated at dive start; ≥ 0. |
| `otu_end` | number | O | OTU accumulated at dive end; ≥ 0. |
| `surface_pressure` | number | O | Bar; 0.4–1.2 (ambient pressure at the 6500 m altitude ceiling is ≈ 0.44 bar). Ambient surface pressure the computer used. |
| `entry_position` | Position | O | Where the diver entered the water. |
| `exit_position` | Position | O | Where the diver surfaced. |
| `trip_uuid` | uuid | O | → `trips`. |
| `course_uuid` | uuid | O | → `courses` (§6.17). The training course this dive was logged on. |
| `site_uuids` | array of uuid | O | → `sites`; the first element is the primary site, the remaining order is the diver's own (§5.3). |
| `gear_uuids` | array of uuid | O | → `gear`; the diver's own order. |
| `species_uuids` | array of uuid | O | → `species`; the diver's own order. |
| `cylinders` | array of Cylinder | O | §6.3, in the diver's own cylinder order. |
| `source_file` | Stored File | O | §6.7 — the original dive-computer file this dive was imported from. |
| `profile` | Profile | O | §6.4. |
| `created_at` | date-time | O | §5.7. |


### 6.3 Cylinder

One cylinder (or other gas source) on one dive. Embedded in the dive; no uuid. **An
entry is one gas supply as the diver manages it**: a manifolded twinset is one entry
with the combined water capacity (a D12 is `volume: 24.0`), while two sidemount bottles
carrying the same trimix are two entries, each with its own pressures — entries are gas
supplies, not distinct blends. An entry converted from a mix-only source
(a UDDF `mix`, a configured gas-list slot) is a cylinder with its vessel members absent,
per §5.4 — nothing invented, nothing required.

| member | type | presence | constraints / meaning |
| --- | --- | --- | --- |
| `volume` | number | O | Liters of water capacity; > 0. |
| `start_pressure` | number | O | Bar; > 0 and ≤ 350. A recorded 0 start pressure is not a measurement, it is a device's absent-marker — writers MUST NOT emit it (§5.4). |
| `end_pressure` | number | O | Bar; ≥ 0 and ≤ 350. `0` is legal here (an out-of-gas ascent is a recorded fact). |
| `oxygen` | number | O | Percent; 0–100. **Absent means not recorded, not 21** — readers MUST NOT assume air (§5.4). |
| `helium` | number | O | Percent; 0–100. |
| `po2_limit` | number | O | Bar; 0.4–2.0. The planned pO₂ ceiling for this gas. |
| `gas_number` | integer | O | ≥ 0. The dive computer's own label for this gas, scoped to this dive — **a label, not an array index**; some devices number from 0, some from 1. It is the join key to `profile.pressures[].gas_number` and to `gas_switch` events. |
| `role` | string | O | One of `"bottom"`, `"deco"`, `"diluent"`, `"oxygen"`. |
| `usage` | string | O | One of `"parallel"` (breathed alongside others, e.g. sidemount pairs), `"staged"` (carried for a later phase). |

When both pressures are present, `end_pressure` MUST be ≤ `start_pressure`. When both
fractions are present, `oxygen + helium` MUST be ≤ 100 — the remainder is treated as
nitrogen; the ~1 % of argon and trace gases in air is not modeled, matching
dive-planning convention.

### 6.4 Profile

The sampled record of a dive, embedded in the dive.

| member | type | presence | constraints / meaning |
| --- | --- | --- | --- |
| `duration` | integer | R | Seconds spanned by the profile's **samples**; ≥ 0, and MUST be ≥ the largest `times` entry in any channel. An event `time` MAY fall outside it — see below. MAY differ from the dive's logged `duration` — a gap after the last sample is real: a computer that stops *sampling* at the surface can keep *timing* the dive. |
| `depth` | Series | O | Samples in **centimeters** (§5.1). |
| `ceiling` | Series | O | Decompression ceiling, in **centimeters**. Present only while a ceiling existed: a gap in `times` means "no deco obligation", not a sensor dropout — and readers MUST NOT interpolate across a ceiling gap, which would fabricate an obligation that was not there. |
| `temperature` | Series | O | Samples in **tenths of a degree Celsius**. |
| `pressures` | array of Pressure Series | O | One entry per monitored cylinder; samples in **tenths of a bar**. |
| `events` | array of Event | O | In time order. |

**An event may fall after the last sample, and readers MUST preserve it where it is.**
`duration` spans the samples, so an event `time` greater than `duration` is conforming and
means exactly what it says: the event happened then. Dive computers produce this routinely
— a diver presses a marker button at the surface after the recorder has written its final
sample, and the marker is real logbook data. A reader MUST NOT clamp such an event to
`duration`, drop it, or extend `duration` to swallow it: the first two destroy a recorded
fact and the third invents a sample span the file never had, which §5.4 forbids. A reader
that plots a profile clips to its own axis rather than rescaling the data.

The integer scales are load-bearing, not stylistic: integers make round-trip
bit-fidelity unconditional — no dependence on any writer's float formatting — which is
this format's first principle applied to its bulkiest data.

### 6.5 Series and Pressure Series

A **Series** is `{"times": [...], "values": [...]}`: two parallel integer arrays.
`times` holds elapsed seconds from the start of the dive, ≥ 0 and **strictly
increasing**; `values` holds the readings in the channel's scale. The arrays MUST be the
same length and MUST NOT contain nulls — a sensor dropout is a gap in `times`, never a
null in `values`. Sampling MAY be irregular; readers MUST NOT assume a fixed interval.

A **Pressure Series** is a Series plus `gas_number` (integer, REQUIRED, ≥ 0): the
device's label tying this cylinder's channel to the dive's cylinders and gas-switch
events. The correspondence to a `cylinders` entry with the same `gas_number` SHOULD hold
but is not guaranteed — a device can report a channel for a transmitter the diver never
described as a cylinder.

### 6.6 Event

A point event on the profile timeline.

| member | type | presence | constraints / meaning |
| --- | --- | --- | --- |
| `time` | integer | R | Elapsed seconds from dive start; ≥ 0. |
| `type` | string | R | One of `"gas_switch"`, `"deep_stop"`, `"safety_stop"`, `"bookmark"`, `"other"`. |
| `gas_number` | integer | O | On a `gas_switch`: what was switched to, in the device's own labeling (§6.3). Absent when the device recorded a switch without saying to what. |
| `label` | string | O | The device's own wording. On `type: "other"` it is REQUIRED and MUST NOT be null — an unclassified event with no label carries no information at all. |

### 6.7 Stored File

Metadata for a binary the source logbook stores — a dive computer's original export file,
or a scan of a certification card. The bytes themselves are not in the document; inside
an archive (Appendix A) they travel as members of the container.

| member | type | presence | constraints / meaning |
| --- | --- | --- | --- |
| `uuid` | uuid | R | |
| `original_filename` | string | R | ≤ 255. As the diver uploaded it. |
| `content_type` | string | R | ≤ 64. The stored media type. |
| `byte_size` | integer | R | ≥ 0. |
| `sha256` | string | R | Lowercase hex SHA-256 of the stored bytes — 64 characters. This is the digest of the bytes as stored in the source system, so a restored copy can be verified end-to-end. |
| `archive_path` | string | O | Inside an archive: the container-relative path of the bytes (Appendix A). In a bare document: absent — there is no container for it to point into. |

The reference implementation records which of its parsers understood a dive-computer file
under its producer key (`"extensions": {"opendiving": {"parser_key": "suunto_json"}}`);
parser registries are application-specific and have no core member.

### 6.8 Trip

| member | type | presence | constraints / meaning |
| --- | --- | --- | --- |
| `uuid` | uuid | R | |
| `name` | string | R | 1–255. |
| `locations` | array of Trip Location | O | In the diver's own order. |
| `starts_on` | date | R | |
| `ends_on` | date | O | MUST be ≥ `starts_on`. Absent when no end is recorded — an ongoing trip, or one logged with only its start. |
| `notes` | string | O | ≤ 10000. |
| `created_at` | date-time | O | §5.7. |

### 6.9 Trip Location

A named place a trip went. Embedded value object; no uuid.

| member | type | presence | constraints / meaning |
| --- | --- | --- | --- |
| `name` | string | R | 1–255. |
| `display_name` | string | O | ≤ 512. A fuller geocoded form of the name. |
| `position` | Position | O | §6's Position object. |
| `bbox` | Bounding Box | O | The geocoded extent of the named place — the rectangle a geocoder returned for it, so a reader can frame a map around the whole area without re-geocoding. Requires `position`. |

A **Bounding Box** is an object with four REQUIRED number members — `south` and `north`
(−90 to 90), `west` and `east` (−180 to 180). `south` MUST be ≤ `north`; `west` MAY
exceed `east`, which means the box crosses the antimeridian. A location with a bare
`name` and nothing else is fully conforming — a place the diver named but no geocoder
resolved.

### 6.10 Dive Site

| member | type | presence | constraints / meaning |
| --- | --- | --- | --- |
| `uuid` | uuid | R | |
| `name` | string | R | 1–255. |
| `location` | string | O | ≤ 255. Free-text locality ("Las Galletas, Tenerife"). |
| `position` | Position | O | §6's Position object. |
| `notes` | string | O | ≤ 10000. |
| `created_at` | date-time | O | §5.7. |

### 6.11 Species

A marine species the diver has sighted. Species records are a projection of the source
application's catalog, limited to what the document's dives reference.

| member | type | presence | constraints / meaning |
| --- | --- | --- | --- |
| `uuid` | uuid | R | The document-internal identity dives reference. |
| `aphia_id` | integer | O | > 0. The WoRMS AphiaID — **the interchange identity**. A uuid means nothing outside its logbook; an AphiaID names the same taxon everywhere. |
| `scientific_name` | string | O | 1–255. |
| `common_name` | string | O | 1–255. |
| `rank` | string | O | ≤ 64. WoRMS's open vocabulary (`"Species"`, `"Genus"`, `"Family"`, …) — not an enum. |
| `wikidata_qid` | string | O | ≤ 32, e.g. `"Q1126155"`. The Wikidata item for the taxon — a secondary interchange identity linking onward to Commons imagery and cross-references; AphiaID remains the matching key. |
| `created_at` | date-time | O | §5.7. |

A species record MUST carry at least one of `aphia_id`, `scientific_name`,
`common_name`, or `wikidata_qid` — an identity-less sighting is uninterpretable, but a
sighting logged by common name alone is real logbook data a converter must be able to
carry, and each identity member that can satisfy this rule requires at least one
character, so an empty string can never stand in for an identity.

A reader with its own species catalog matches on `aphia_id`, not on names and never on
`uuid`; a record without one simply doesn't match. The embedded record exists so the
document is readable without a WoRMS connection; it is a snapshot, not an authority — a
reader maintaining a catalog SHOULD resolve unknown AphiaIDs against WoRMS rather than
create catalog entries from the snapshot.

### 6.12 Gear Item

| member | type | presence | constraints / meaning |
| --- | --- | --- | --- |
| `uuid` | uuid | R | |
| `name` | string | R | 1–255. |
| `brand` | string | O | ≤ 255. |
| `type` | string | O | One of `"mask"`, `"snorkel"`, `"fins"`, `"wetsuit"`, `"drysuit"`, `"vest"`, `"hood"`, `"gloves"`, `"boots"`, `"bcd"`, `"regulator"`, `"computer"`, `"cylinder"`, `"light"`, `"smb"`, `"mirror"`, `"whistle"`, `"reel"`, `"knife"`, `"line_cutter"`, `"shears"`, `"compass"`, `"camera"`, `"other"`. An OPTIONAL member, so this vocabulary can grow in minor versions (§7) — an air horn rides `"other"` until it earns a value. |
| `notes` | string | O | ≤ 10000. |
| `rented` | boolean | O | |
| `archived` | boolean | O | Retired from active use. |
| `archived_at` | date-time | O | |
| `dive_count` | integer | O | ≥ 0. **Derived** (§5.7): the item's use count in the source logbook. |
| `created_at` | date-time | O | §5.7. |

### 6.13 Gear Set

A named bundle of gear items the diver equips together.

| member | type | presence | constraints / meaning |
| --- | --- | --- | --- |
| `uuid` | uuid | R | |
| `name` | string | R | 1–255. |
| `weight` | number | O | Kilograms of ballast the set implies; ≥ 0. |
| `gear_uuids` | array of uuid | O | → `gear`, in the set's own order. |
| `created_at` | date-time | O | §5.7. |

### 6.14 Service Schedule

A recurring maintenance rule for a gear item.

| member | type | presence | constraints / meaning |
| --- | --- | --- | --- |
| `uuid` | uuid | R | |
| `gear_uuid` | uuid | R | → `gear`. |
| `type` | string | R | One of `"service"`, `"visual_inspection"`, `"hydrostatic_test"`, `"battery"`, `"oxygen_clean"`, `"other"`. |
| `label` | string | O | ≤ 120. Distinguishes multiple rules of one type. |
| `starts_on` | date | R | When the rule's clock starts. |
| `interval_months` | integer | O | > 0. |
| `interval_dives` | integer | O | > 0. At least one of the two intervals MUST be present. |
| `dive_count_at_start` | integer | O | ≥ 0. **Snapshot** (§5.7): the item's lifetime use count when the rule started — the baseline `interval_dives` counts from. |
| `active` | boolean | O | |
| `last_service_on` | date | O | **Derived** (§5.7). |
| `next_due_on` | date | O | **Derived** (§5.7). |
| `next_due_at_dive_count` | integer | O | **Derived** (§5.7): the lifetime count at which service falls due — a threshold, not a remaining count. |
| `created_at` | date-time | O | §5.7. |

### 6.15 Service Record

One performed maintenance event.

| member | type | presence | constraints / meaning |
| --- | --- | --- | --- |
| `uuid` | uuid | R | |
| `gear_uuid` | uuid | R | → `gear`. |
| `gear_service_schedule_uuid` | uuid | O | → `gear_service_schedules`. Absent when the record predates its rule or the rule was deleted — history outlives the rule. |
| `type` | string | R | Same vocabulary as §6.14; copied at write time so it survives the schedule's deletion. |
| `serviced_on` | date | R | |
| `dive_count_at_service` | integer | O | ≥ 0. **Snapshot** (§5.7). |
| `label` | string | O | ≤ 120. |
| `performed_by` | string | O | ≤ 255. |
| `notes` | string | O | ≤ 10000. |
| `created_at` | date-time | O | §5.7. |

### 6.16 Certification

| member | type | presence | constraints / meaning |
| --- | --- | --- | --- |
| `uuid` | uuid | R | |
| `agency` | string | R | One of `"padi"`, `"ssi"`, `"naui"`, `"sdi"`, `"tdi"`, `"cmas"`, `"raid"`, `"bsac"`, `"gue"`, `"iantd"`, `"psai"`, `"dan"`, `"efr"`, `"andi"`, `"snsi"`, `"acuc"`, `"pss"`, `"ida"`, `"other"`. This vocabulary is REQUIRED-member frozen after 1.0 (§7), which is why it was seeded wide; national CMAS federations are `"cmas"`. |
| `agency_other` | string | O | ≤ 64. REQUIRED when `agency` is `"other"`; MUST be absent otherwise. |
| `name` | string | R | 1–255. The certification's name, free text on purpose — agency catalogs are unbounded. |
| `certification_number` | string | O | ≤ 64. |
| `certified_on` | date | O | |
| `expires_on` | date | O | |
| `instructor_name` | string | O | ≤ 255. |
| `instructor_number` | string | O | ≤ 64. |
| `training_center` | string | O | ≤ 255. |
| `course_uuid` | uuid | O | → `courses` (§6.17). The course this card came out of. One course can issue several certifications; a certification names at most one course. |
| `notes` | string | O | ≤ 10000. |
| `front_file` | Stored File | O | §6.7 — the scan of the card's front. A card has one front and one back, so the members say so; an array with a side discriminator would let a document claim two fronts. |
| `back_file` | Stored File | O | §6.7. |
| `created_at` | date-time | O | §5.7. |

### 6.17 Course

A training course. The course carries no list of its dives or certifications — the
links live on the children (`dives[].course_uuid`, `certifications[].course_uuid`), and
a reader rebuilds the grouping by walking them, the same direction as trips: the course
is the thing that keeps existing when a dive is deleted. One course can issue several
certifications (combined-card programs exist); a dive or certification names at most
one course.

| member | type | presence | constraints / meaning |
| --- | --- | --- | --- |
| `uuid` | uuid | R | |
| `name` | string | R | 1–255. |
| `agency` | string | R | The same vocabulary as §6.16's `agency`, shared deliberately — a course and the cards it issued can never name the same agency two ways. The same freeze rule applies (§7). |
| `agency_other` | string | O | ≤ 64. REQUIRED when `agency` is `"other"`; MUST be absent otherwise — §6.16's pairing rule. |
| `status` | string | O | One of `"planned"`, `"in_progress"`, `"completed"`, `"incomplete"`, `"provisional"`, `"not_passed"` — a booked course exists before its first dive, a referral leaves one open for months, and some agencies issue provisional passes. Absent means not recorded; readers MUST NOT assume `"completed"` (§5.4). |
| `starts_on` | date | O | |
| `ends_on` | date | O | MUST be ≥ `starts_on` when both are present. Each date is independently optional — a planned course has no dates yet, a referral course spans months with fuzzy edges, and a course with only one known date is a real state. |
| `instructor_name` | string | O | ≤ 255. |
| `instructor_number` | string | O | ≤ 64. |
| `training_center` | string | O | ≤ 255. The same trio as §6.16's, duplicated deliberately rather than normalized away: imported history arrives certification-first, with no course to hang the fields on, so a certification stands alone. |
| `notes` | string | O | ≤ 10000. |
| `created_at` | date-time | O | §5.7. |

## 7. Versioning

A document declares the specification version it conforms to in its `version` member, as
`"major.minor"`. The policy:

- **Minor versions are strictly additive.** `1.(n+1)` may define new OPTIONAL members
  and, in OPTIONAL members only, new enum values; it MUST NOT remove a member, change a
  member's type, meaning, or units, tighten a constraint, or add values to the
  vocabulary of a REQUIRED member — a reader's only safe response to an unknown value is
  treating the member as absent (§5.6), which a REQUIRED member cannot survive. REQUIRED
  vocabularies grow only through their existing `"other"` values, or at a major version.
  Under these rules everything a conforming `1.n` reader does with a `1.(n+1)` document
  remains correct.
- **A reader accepts any document whose major version it implements**, whatever the
  minor. A reader MUST reject, or clearly flag as unsupported, a document whose major
  version it does not implement.
- **A writer declares exactly the lowest version that defines everything it emitted.**
- A major version may break anything, and is expected never to be needed: the additive
  rules above, the growable OPTIONAL vocabularies, and the `extensions` mechanism exist
  precisely so the format can grow without one. Implementers can treat 1.x as stable
  forever; a major would mean this design failed.

Each minor version publishes its own JSON Schema; §3 defines the schema's per-version
scope.

## 8. Media type and file extension

The media type for DiveJSON is `application/vnd.dive+json`. The `+json` structured-syntax
suffix applies: absent specific knowledge of DiveJSON, processors may treat a document as
generic JSON [RFC 8259]. There are no media-type parameters; the encoding is always
UTF-8.

The RECOMMENDED file extension is **`.divejson`**. On platforms that require one, the
Macintosh file type code is `TEXT`.

Registration of the media type in the IANA vendor tree (per [RFC 6838] §3.2) is planned
for when this specification freezes at 1.0, naming <https://divejson.org> as the
published specification; until the registration completes, the type is used as declared
here. The registration template's required security section is §9 of this document.

## 9. Security considerations

DiveJSON shares the security considerations of JSON [RFC 8259]. A document contains no
executable content, no external references that a processor is required to dereference,
and no processing instructions; readers MUST NOT execute or dereference anything found in
one. Beyond generic JSON concerns:

- **A DiveJSON document is a personal dossier.** By design it is a *complete* logbook:
  precise timestamped positions (dive-site coordinates, per-dive entry/exit satellite
  fixes, trip bounding boxes) that together form a movement history; the diver's name,
  handle, and email address; certification numbers, instructor names, and training
  centers, which function as identity documents; and free-text notes of up to 10,000
  characters on six record types. Software handling documents SHOULD treat them with the
  care of a personal data export: serve them only to their owner, over authenticated
  channels, without shared caching.
- **Archives raise the stakes** (Appendix A): they add the referenced binaries, which can
  include scans of certification cards — ID-like personal documents — and, among
  producer-added members, even a profile photo (the reference implementation ships the
  diver's avatar in its archives). Extraction of third-party archives MUST treat member paths as untrusted (reject
  absolute paths and `..` traversal), and SHOULD verify each extracted file against its
  `sha256` before use.
- **Numeric and size limits.** Documents can be large — a sampled profile per dive,
  thousands of dives; instructors' and divemasters' logbooks run five figures. Readers SHOULD bound memory (streaming or spooled parsing, input
  size caps) and MUST NOT let unexpected magnitudes in numeric members index or allocate
  unchecked.
- **Re-rendering text.** Free-text members are arbitrary user content. Software
  re-rendering them into HTML must escape them; software exporting them into spreadsheet
  formats should neutralize formula-leading characters (`=`, `+`, `-`, `@`) — a document
  produced by an attacker and re-exported as CSV is a formula-injection vector.
- **Digests correlate.** `sha256` values let anyone holding two documents prove they
  reference identical files. This is the mechanism working as intended (end-to-end
  restore verification) but is worth knowing when publishing documents.
- **Duplicate JSON member names** are not conforming JSON-for-interchange; readers SHOULD
  reject documents containing them rather than let two parsers disagree about the
  winning value.

## Appendix A. The archive convention (informative)

A DiveJSON document describes stored files (§6.7) but does not contain their bytes. The
archive convention packages both: a ZIP container in which

- the member `logbook.divejson` at the container root is a DiveJSON document, and
- every stored-file record whose bytes are included names, in its `archive_path`, the
  container-relative path of the member holding those bytes.

The document itself is the manifest — there is no separate manifest member. An
`archive_path` is relative, uses `/` separators, and never contains `.` or `..`
components; a record without `archive_path` is metadata whose bytes the
container does not carry. Each included member's bytes hash to the record's `sha256`.

A producer MAY include additional members (the reference implementation adds a UDDF
rendering, CSV views, and the diver's avatar image); consumers of the convention ignore
members the document does not reference. The RECOMMENDED extension for the container is
`.zip`, and the container carries no DiveJSON-specific media type.

## Appendix B. Example (informative)

A minimal but realistic document — one dive with a cylinder and a short profile, its
site, and the diver:

```json
{
  "format": "divejson",
  "version": "1.0",
  "exported_at": "2026-08-28T10:15:00+00:00",
  "generator": { "name": "Example Logbook", "version": "2.4.0" },
  "diver": {
    "uuid": "019fec35-54b9-7874-a1c7-b504a3e8e778",
    "name": "Sam Reef"
  },
  "dives": [
    {
      "uuid": "019fec36-b9ec-71c6-a03e-64f59b8b92b1",
      "dive_number": 42,
      "started_at": "2026-04-17T11:49:23+02:00",
      "duration": 2460,
      "max_depth": 18.4,
      "water_type": "salt",
      "site_uuids": ["019fec36-b8b8-7cc9-a4b9-ede85f907c94"],
      "cylinders": [
        { "volume": 12.0, "start_pressure": 200.0, "end_pressure": 70.0, "oxygen": 32.0 }
      ],
      "profile": {
        "duration": 2460,
        "depth": { "times": [0, 60, 120, 2400], "values": [0, 950, 1840, 310] },
        "temperature": { "times": [0, 1200], "values": [261, 224] },
        "events": [{ "time": 2100, "type": "safety_stop" }]
      }
    }
  ],
  "sites": [
    {
      "uuid": "019fec36-b8b8-7cc9-a4b9-ede85f907c94",
      "name": "House Reef",
      "location": "Dahab, Egypt",
      "position": { "latitude": 28.567251, "longitude": 34.533257 }
    }
  ]
}
```

## References

- [RFC 2119] Bradner, S., "Key words for use in RFCs to Indicate Requirement Levels",
  BCP 14, RFC 2119, March 1997. <https://www.rfc-editor.org/rfc/rfc2119>
- [RFC 8174] Leiba, B., "Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words",
  BCP 14, RFC 8174, May 2017. <https://www.rfc-editor.org/rfc/rfc8174>
- [RFC 8259] Bray, T., Ed., "The JavaScript Object Notation (JSON) Data Interchange
  Format", STD 90, RFC 8259, December 2017. <https://www.rfc-editor.org/rfc/rfc8259>
- [RFC 3339] Klyne, G. and C. Newman, "Date and Time on the Internet: Timestamps",
  RFC 3339, July 2002. <https://www.rfc-editor.org/rfc/rfc3339>
- [RFC 9562] Davis, K., Peabody, B., and P. Leach, "Universally Unique IDentifiers
  (UUIDs)", RFC 9562, May 2024. <https://www.rfc-editor.org/rfc/rfc9562>
- [RFC 6838] Freed, N., Klensin, J., and T. Hansen, "Media Type Specifications and
  Registration Procedures", BCP 13, RFC 6838, January 2013.
  <https://www.rfc-editor.org/rfc/rfc6838>
- JSON Schema: A Media Type for Describing JSON Documents, draft 2020-12.
  <https://json-schema.org/specification>
- WoRMS — World Register of Marine Species. <https://www.marinespecies.org/>
- EN 13319:2000, "Diving accessories — Depth gauges and combined depth and time measuring
  devices — Functional and safety requirements, test methods".
