# Writing DiveJSON as UDDF

**Non-normative.** The specification is [`spec/divejson.md`](../spec/divejson.md); nothing
here changes what a conforming document is. [`uddf-mapping.md`](uddf-mapping.md) is the
other direction — every element a reader takes into DiveJSON — and this document is what a
writer does with a DiveJSON document that has to become a UDDF file: which member lands in
which element, what UDDF has no room for, and what a reader will make of each thing that
did not fit.

The rules a writer follows whatever format it is writing are in
[`writing.md`](writing.md) — how a writer is checked, the three answers to a required
element the document has nothing for, the report's kinds read on the way out, and a
writer being a function of its input — and the rules that hold in **either** direction are
in [`converting.md`](converting.md), identity among them. Neither is repeated here. This
document carries what is UDDF's, and keeps beside each general rule the example that first
showed it.

## Why write UDDF at all

Because it is what the rest of the world opens. Subsurface, divelogs.de and MacDive read
UDDF, and a diver whose logbook is DiveJSON needs a file they can hand to a dive shop, load
into a desktop application, or upload — the same reason the reading direction exists,
pointed the other way.

DiveJSON's own **reference writer** is the application the format came out of, and it stays
the reference: this is a second writer serving applications that are not that one, not a
replacement for it. The two agree on everything a logbook actually holds, and differ wherever
an application exporting its own data and a converter producing an interchange file want
opposite things. **Each such place is marked "Differs from the reference writer" below**, and
those markers are the list — no count of them is stated anywhere, a figure kept away from the
thing it counts being a second place for it to be wrong.

## What a correct writer is checked against

The three checks are `writing.md`'s. What is UDDF's is how each one lands here.

**The pairs are compared as canonical XML with `<generator>` ignored**, which is this
format's answer to the general question of how two of its files are compared when one was
produced just now: two runs of one writer differ in the version stamped there and in nothing
else. [`fixtures/write/uddf/`](../fixtures/write/uddf) holds them and `divejson conform` runs
them; what each covers is in [`fixtures/README.md`](../fixtures/README.md#writeuddf).

**The self round trip** reads a written file back through a UDDF reader and expects the
document it was written from, on every member [`uddf-mapping.md`](uddf-mapping.md)'s element
map carries. This document is the description of what does not come back.

**`extensions` is the exclusion this direction adds** to the two the corpus already ignores
(`writing.md`), and UDDF is where it is visible: `<generator>` and `/uddf/@version` describe
the file in front of a reader, which after a write is the one this writer produced, so the
source's own generator and declared version stay behind.

**The XSD is the check the corpus cannot make.** UDDF 3.2.2 has one, so validating output
against it belongs in an implementation's own suite — and here it is the only check that can
see element **order**, which is a live hazard in this format: `informationbeforedive`,
`waypoint`, `equipment`, `tankdata` and `trippart` are all `xs:sequence`, so a member added
in the wrong place produces a file a lenient reader — including this format's own, which
takes children by name — is perfectly happy with and no other implementation can open.

## The three answers, in UDDF

`writing.md` states them: write the format's own spelling for "not recorded", or drop the
value and report it, and never invent. UDDF is a clean example of the distinction that
decides between the first two, because it has both shapes as **mandatory** elements.

`<greatestdepth>` is mandatory and its `0` *is* the format's spelling for absence, so it is
written and a reader takes it straight back off. `<geography><location>` is mandatory and a
place name has no such spelling — so a site with coordinates and no `location` loses the
coordinates rather than having its own **name** copied into a member that means something
else. A round trip through that would hand the diver back a location they never wrote.

## The report, going out

`writing.md` has the kinds and what a `where` is. In this format `absent` is an element UDDF
requires that the document had nothing for, and `dropped` is a member UDDF has nowhere to
put; the paths are `dives/0`, `dives/0/cylinders/1`, `trips/0/locations/1` and `$`.

A member with nowhere to go is reported from the record itself and not from a list
(`writing.md`), so **the tables below are a description of what a writer does and not the
source of it** — the next member §6 gains reports itself here rather than going silently.

## The element map

Read `uddf-mapping.md`'s map backwards for everything not called out here — the rows are the
same rows. What follows is only where writing is not simply reading in reverse.

### Document

| DiveJSON | UDDF |
| --- | --- |
| — | `/uddf/@version` — `3.2.2`, the schema written against |
| `generator` | not carried; `/uddf/generator` names **the writer** |
| `exported_at` | `/uddf/generator/datetime` |
| `extensions` | not carried — see above |

`<generator><type>` is `converter`, which is one of the three values `generatorType`
enumerates. The reference writer says `logbook`, being one.

**`<generator><datetime>` is the document's own `exported_at` and never the clock**, which
is where `writing.md`'s function-of-its-input rule lands in this format: the only thing left
moving between two writes of one document is the version stamped beside it, which is exactly
what the pair comparison ignores.

### Identity

Ids are written `<kind>-<uuid>` — `dive-019fec36-b9ec-71c6-a03e-64f59b8b92b1` — because
`xs:ID` is an `NCName` and cannot begin with a digit, which a hex UUID regularly does.
`converting.md`'s identity rule reads a short alphabetic prefix back off, so an id written
this way returns as the UUID it was and a logbook that went out through UDDF comes back with
the identities it left with. The prefixes are `dive`, `site`, `trip`, `gear`, `diver` and
`mfr`.

`<owner id>` is `diver-<uuid>` where the document names a person and the bare string `owner`
otherwise — the latter being what every UDDF writer in the corpus emits and what a reader is
careful never to read as an identity.

### Diver and gear

A document's gear lives inside `<diver><owner><equipment>`, so `<diver>` is written whenever
there is either an owner to describe **or** a piece of kit to hang on one. An owner the
document says nothing about gets empty `<firstname>`/`<lastname>` elements, which are valid
`xs:string`s that a reader takes as no diver at all.

`personalType` requires a first and last name where DiveJSON holds one string: the first
whitespace-separated token becomes the given name and the remainder the family name, and a
one-token name leaves `<lastname>` **empty** rather than repeating the given name. A reader
joins them back with a space, so any split survives.

**Differs from the reference writer**: `diver.email` is written to
`<contact><email>`. The reference writer deliberately omits it — a UDDF file is the thing a
diver hands to a dive shop, and their address riding along in it would be a surprise — which
is the right call for an application exporting on a diver's behalf and the wrong one for a
library asked to write the document it was given.

Gear types land in `equipmentType`'s elements. A type UDDF's own vocabulary does not name
goes to **`<variouspieces>`**, its catch-all, which a reader maps back to `other`; that is
the same translation a reader makes for `<scooter>` and `<lead>` in the other direction, and
it is reported, since the type did not survive.

| `gear.type` | UDDF element | comes back as |
| --- | --- | --- |
| `mask`, `fins`, `gloves`, `boots`, `compass`, `knife`, `light`, `regulator` | the same name | itself |
| `bcd` | `buoyancycontroldevice` | itself |
| `computer` | `divecomputer` | itself |
| `cylinder` | `tank` | itself |
| `wetsuit`, `drysuit` | `suit`, with `<suittype>` | itself |
| `other` | `variouspieces` | itself |
| `snorkel`, `vest`, `hood`, `smb`, `mirror`, `whistle`, `reel`, `camera`, `line_cutter`, `shears` | `variouspieces` | `other` |

`camera` is in the last row for a schema reason rather than a vocabulary one: `cameraType`
extends `ID_TYPE` rather than `namedType`, so a `<camera>` has no `<name>` at all and could
carry only a nameless body-and-lens breakdown.

**Differs from the reference writer**: it sends `line_cutter` and `shears` to `<knife>`, on
the grounds that they are cutting tools and that scattering a diver's cutting tools into the
catch-all beside the SMB reads worse. A converter does not, because `<knife>` asserts a
knife where `<variouspieces>` asserts nothing — losing a type honestly beats substituting a
near one, and the report is what makes the loss visible either way.

**`equipmentType` is an `xs:sequence`, so a logbook's gear comes back grouped by type**
rather than in the order the document listed it. Nothing is lost by that — every piece keeps
its uuid — so it carries no finding.

### Sites and trips

`geographyType` makes `<location>` mandatory, so **coordinates are written only where the
record has a place name**: a site with a `position` and no `location`, or a trip location
with a `position` and no `display_name`, keeps its name and loses its coordinates, reported.

**Differs from the reference writer**: it puts the record's own **name** in `<location>` and
keeps the coordinates, which is defensible for an application exporting data it holds a name
for and wrong for a converter — a round trip through it hands the diver back a `location`
they never wrote. This is the same trade *The three answers* describes, and it is the one
place in the document where the reference writer takes the third of them.

A trip becomes one `<trippart>` **per §6.9 location**, which is the only shape a list of
places fits: a reader takes a trip's span as the span of its parts and its locations from
their names, so a part per location comes back as the list it was written from. A trip with
no locations still needs one part — `tripType` requires at least one — and gets a nameless
one, an empty `<name>` being a valid `xs:string` that reads back as no location rather than
as one. The trip's dates and its note go on the **first** part, since a reader takes the
span of every part's dates and joins every part's notes.

`<dateoftrip>`'s `startdate` and `enddate` are both `use="required"` and both `xs:dateTime`
where DiveJSON holds plain dates, so each is widened to midnight and a reader takes the date
back off the front. A trip with no `ends_on` has nothing for `enddate`: **the start date is
repeated**, reported, and a reader sees a trip that ended the day it began. UDDF has no
spelling for an open one.

`trips[].locations[].bbox` has no UDDF slot at all.

### Dives

`<divenumber>` is an `xs:positiveInteger` where §6.2 puts no floor under `dive_number`, so a
dive numbered 0 or below is written **without** one and reported. A zero there would make
the whole document invalid, which is a file nobody can open rather than a dive nobody can
number.

`<greatestdepth>` and `<diveduration>` are both mandatory where `max_depth` and `duration`
are optional. Both take **`0`**, reported: the schema excludes zero from each of those
members, so a reader takes the zero back as "not recorded" rather than as the surface or as
a dive of no length.

`informationbeforediveType` is an `xs:sequence`: `<link>`s first, then `<divenumber>`,
`<datetime>`, `<altitude>`, `<equipmentused>`, `<tripmembership>`, `<surfacepressure>`.
`informationafterdiveType` is an `xs:all` and its order is free.

`started_at` is written **exactly as recorded**, offset and sub-second fraction and all;
§5.2's rule that an offset is never supplied applies as much to a writer as to a reader.

Members with no UDDF slot anywhere: `water_type`, `cns_start`, `cns_end`, `otu_start`,
`otu_end`, `entry_position`, `exit_position`, `course_uuid`, `species_uuids`, `source_file`,
`created_at`.

### Cylinders and gases

`<tankpressurebegin>` is mandatory where `start_pressure` is optional, and takes **`0`** —
which §6.3 names as the absent-marker devices write and a reader reads back as not
recorded. The cylinder therefore keeps its size and its gas.

**Differs from the reference writer**: it omits the whole `<tankdata>` for a cylinder with
no start pressure, having a `logbook.divejson` beside the export to keep the cylinder in. A
converter has no such second file.

**A cylinder gets a `<mix>` of its own within its dive.** Gases deduplicate across the
logbook — a hundred air dives share one `<mix>` — but two cylinders of *one* dive never
share, even carrying an identical blend. `<tankpressure ref>` and `<switchmix ref>` address
a **mix** rather than a cylinder, and a reader resolves a shared reference positionally, so
a sidemount pair on one blend would come back with its two pressure channels crossed the
moment one of them missed a waypoint the other had.

A cylinder whose gas the document never recorded still gets a `<mix>`, carrying a `<name>`
of `unrecorded` and no `<o2>` at all — which is how UDDF says nothing about a gas, and what
gives that cylinder's pressure channel something valid to point at. "No mix recorded" and
"air" are different gases and one `<mix>` cannot be both.

`<mix>` fractions are 0–1 where §6.3 holds percentages; `<maximumpo2>` is bar in both.
`<mix><n2>`, `<ar>` and `<h2>` are not written: §6.3 models the remainder as nitrogen and
does not model argon or trace gases.

`cylinders[].role` and `cylinders[].usage` have no UDDF slot — the format has no manifold or
sidemount representation at all, so there is nothing to write `usage` into.

**UDDF records no cylinder numbering.** A reader recovers one by counting `<tankdata>`
elements in file order, and only where the profile asks for a numbering — a pressure
channel, or a gas switch naming the cylinder it switched to. So `gas_number` survives in
exactly one case: numbered from 0 by position, on a dive whose profile needs a numbering.
Anything else — a label that is not its position, or a dive with no profile at all — is
reported, there being nowhere in the file to put it.

### Profiles

**Every reading keeps its own second.** UDDF puts everything recorded at one instant inside
one `<waypoint>`, so the waypoints are the **union** of every channel's times, and a
waypoint carries only what was measured at that second — a temperature taken between two
depth samples becomes its own waypoint, with a `<divetime>` and a `<temperature>` and no
depth.

**Differs from the reference writer**, and this is the largest of them. It snaps every
other channel onto the depth axis and *drops* a reading that cannot reach a waypoint within
half the depth channel's typical interval, because two importers mishandle a depth-less
waypoint in opposite and equally fatal ways: Subsurface silently discards it (a 706-sample
temperature curve arrived as 29 in one measured case) and divelogs.de reads its missing
depth as **zero**, producing a stored profile that saws between the seabed and the surface
on every other sample. Those are the right trades for a file written *for* those two
consumers and the wrong ones for a file written to be read back, where a dropped reading is
data loss and a moved timestamp is a reading presented as measured where it was not. See
*Known consumer artefacts* below.

`waypointType` is an `xs:sequence`, and the children written go in this order: `<depth>`,
`<divetime>`, `<setmarker>`, `<switchmix>`, `<tankpressure>` (repeatable), `<temperature>`.

Channel units: depth centimetres → metres, temperature tenths of °C → Kelvin, pressures
tenths of a bar → Pascal. Each is a decimal factor, and doing the arithmetic in decimal is
what makes a round trip through Kelvin land back on the number it started from.

`profile.duration` is not written anywhere: UDDF records no duration for a profile, and
§6.4 defines the member as the span of the samples, which a reader takes off them. A
document whose `duration` is not that span is reported.

`profile.ceiling` has no UDDF slot: the only per-waypoint element is `<decostop>`, whose
`@duration` is `use="required"`, and a ceiling sample says how deep the obligation was and
never how long the stop should last.

Events:

| DiveJSON event | UDDF |
| --- | --- |
| `deep_stop`, `safety_stop`, `bookmark` | `<setmarker>` carrying the type as its text |
| `other` with a `label` | `<setmarker>` carrying the label |
| `gas_switch` with a `gas_number` | `<switchmix ref>` naming that cylinder's mix |

Three cases lose something, each reported:

- **An unlabelled `other`** is dropped rather than written as the word "other", which would
  come back as an event labelled "other" — a label the document did not have.
- **A named type carrying a label** keeps the type and loses the label. `<setmarker>` is one
  string with no type beside it, and the three named types are the only thing a round trip
  through it has to go on.
- **A gas switch naming a cylinder this dive does not have** is dropped: `<switchmix ref>`
  is an `xs:IDREF` and there is nothing valid to point it at. Pointing it at another dive's
  mix would say the diver breathed a gas they did not carry.

`waypointType` allows one `<setmarker>` and one `<switchmix>`, so a **second** event of
either kind on one second is dropped and reported.

**Differs from the reference writer**: it joins simultaneous markers with `"; "` rather than
dropping the later one, which is right for a file a human is reading and wrong for one being
read back, where the join returns as a single event whose label is two labels.

## What is never written

The members `uddf-mapping.md` lists as slotless, from the writing side. Each is reported
once per record that carries it, and none of them has anywhere in UDDF to go:

| DiveJSON | why not |
| --- | --- |
| `courses` | `<divetrip>` is the nearest thing and a training course is not a trip; folding one in would make a reader show "PADI Open Water" as a holiday, beside the real trips already there |
| `certifications` | not written — see the note below |
| `gear_sets` | `<equipmentconfiguration>` describes how pieces are rigged together, which is not a named set of them |
| `gear_service_schedules`, `gear_service_records` | not written — see the note below |
| `species` | `<site><ecology>` is site-level flora and fauna where §6.11's species are per-dive sightings |
| a record's `created_at` | no slot on any of them |
| `gear` `rented`, `archived`, `archived_at`, `dive_count` | no slot |
| `diver.username` | `<owner id>` is an XML id and not a handle |
| `trips[].locations[].bbox` | `geographyType` carries a point, not a box |
| a record's `extensions` | producer-defined members (§5.5) |

An **empty** note — `notes: ""` — is not written either: `<para></para>` and no `<notes>` at
all are the same file to every reader, every XML reader here taking an empty element as
absent. It is a value UDDF has no spelling for rather than one a writer chose to drop, and
it is reported.

**Two of those rows are "not written" rather than "no slot", and it is worth being exact
about which.** `uddf-mapping.md`'s *Deliberately not mapped* table groups `courses`,
`certifications`, `gear_sets` and gear service under one reason, which is the right summary
for a **reader**: nothing in the corpus emits any of them, so there is nothing to read.
Going out, the schema does carry `<owner><education><certification>` and a pair of
`<serviceinterval>`/`<nextservicedate>` elements on every equipment piece — neither of which
is what DiveJSON holds (§6.13 keeps a schedule *and* the services performed against it,
where UDDF's two elements are a plan on one piece with no history behind it), and neither of
which any file on record uses. A writer that filled them would be the first to, with no
reader to check the guess against. Mapping either is a change to what the format says it
carries, so it starts in the specification.

## Known consumer artefacts

What a consumer will make of a file written this way, as distinct from what a correct reader
makes of it. Recording them here saves the next reader the round trip; they are the mirror
of `uddf-mapping.md`'s section of the same name.

- **Subsurface discards every depth-less waypoint on import.** A file written here puts a
  reading on its own second, so a temperature or pressure sampled between two depth samples
  is a depth-less waypoint and Subsurface will not keep it. The depth channel arrives whole.
- **divelogs.de reads a missing depth as zero**, so the same waypoints arrive as a profile
  that saws between the real depth and the surface.
- **Subsurface reads no trip element at all**, and the only equipment it reads is the dive
  computer's model. Trips and gear **are** written here — the loss is on the import side,
  in `uddf.xslt`, and not in the encoding.

A writer for a specific consumer rather than for interchange should snap its channels onto
the depth axis the way the reference writer does, and accept the loss that costs. That is a
choice about the consumer, not about the format, which is why it is not this document's
default.
