# Changelog

Notable changes to the DiveJSON specification and its conformance suite. The specification's own
version (`major.minor`, declared in every document) is what readers and writers depend
on; the implementations that read and write it are released separately, from their own
repositories.

## Unreleased

- **Centers are records (§4, §5.3, §5.6, §6.2, §6.9a, §6.15–§6.19, §7, §9).** A course and a
  certification each named the organisation that ran it in a `training_center` string, a
  service record named its shop the same way in `performed_by`, a dive could not say whom it
  was dived with, and a trip part could not say where the diver slept. §6.18's **Center** is
  one record for all of them — the dive center, the school, the shop, the hotel, the boat —
  with a `name`, a set of `roles`, a `phone`, an `email`, a `website`, an `address` and
  `notes`, in a new top-level `centers` collection. §6.19's **Address** is its own object,
  anchored on a REQUIRED `country`, which UDDF's `<address>` requires too. A dive, a course, a
  certification and a service record reference a center through `center_uuid`, and a trip
  part through `accommodation_uuid`: the first reference out of an embedded object, and the
  first not named after its collection, so §5.3 says that an embedded object may reference a
  record and stay a value, and that such a member resolves where its definition says.
  `performed_by` stays, for the person who did the work. §9's dossier names centers and their
  addresses, and lists the record types carrying notes rather than counting them.

  **`roles` is the format's first array of closed values**, because a resort runs dives and
  rents rooms, and a school sells gear. Its vocabulary — `dive_center`, `school`, `shop`,
  `accommodation`, `liveaboard`, `club`, `other` — is OPTIONAL so that it can grow in a minor
  version, and §5.6 and §7 gain the rule that makes that safe: a reader drops an item it does
  not know and keeps the rest, treating the member as absent only when nothing remains. The
  single-value rule applied to a whole array would let one new value erase every value beside
  it.

  **This is a breaking change and it lands inside 1.0**, on the same ground as the ones below.
  It breaks documents: `training_center` is an undefined member on a course and on a
  certification, which the schema rejects, and every fixture carrying it lost it.
  `valid/technical-dive` carries a center with every member, referenced from all five hosts,
  and `valid/demo-logbook` one referenced from the four hosts it has. `fixtures/invalid/` gains
  `accommodation-dangling-reference`, a part's reference to no center, which §3's rule 1 now
  reaches inside a trip; `center-roles-repeated`; and `address-without-country`.

  **UDDF's shapes read into it and it writes back out.** `docs/uddf-mapping.md` reads a
  `<divebase>`, a `<shop>` and a trip part's `<accomodation>` and `<operator>` into centers
  with the role each slot implies, folding the inline ones into the center they name, a
  dive's link to a base or a shop into `center_uuid`, and skips the name-only base Subsurface
  writes into every export. `docs/uddf-writing.md` writes a center to a `<shop>` where that is
  all it is and to a `<divebase>` otherwise, a dive's reference as a link after its site
  links, and a part's as an inline copy, reporting the roles the slots do not say back.
  `fixtures/uddf/centers` is the reading pair, built from the XSD because no export in hand
  carries any of the shapes, and `fixtures/write/uddf/centers` the writing one.

- **A profile's axis is milliseconds (§5.1, §6.4, §6.5, §6.6).** On a whole-second axis a
  converter kept the first of two readings of one channel that rounded to the same second
  and dropped the other, and threw away every sub-second offset its source stated — while
  the Suunto app stamps samples to the millisecond, a freediving computer logs up to four a
  second, and a freedive is a dive. A Series' `times`, a profile's `duration` and an event's
  `time` are now elapsed milliseconds. §5.1 gives the axis a row of its own and keeps seconds
  for a dive's `duration`; `ndl` and `tts` stay seconds, being readings rather than the axis
  they sit on. `docs/converting.md`'s rounding and collision rules hold at the new grain,
  each mapping document states its source's factor, and `docs/uddf-writing.md` writes a
  millisecond that is not a whole second as a fractional `<divetime>`, so a document whose
  samples fall on whole seconds writes no fraction at all.

  **This is a breaking change and it lands inside 1.0**, on the same ground as the ones
  below: the draft's status line lets normative text, schema and fixtures change together
  until the tag, and nothing is tagged. `$id`, `title` and `version` are untouched at `1.0`.
  It breaks documents **silently**. The members keep their names and the schema is
  unchanged, every one of them a non-negative integer before and after, so a document
  written in seconds — any export or conversion made before this change — validates and
  reads a thousand times short. A reader that knows which writer produced a document may read
  that writer's earlier output by that knowledge, which is the reader's business rather than
  §5.6's. Every fixture carrying a profile moved with the unit; `suunto_json/suunto-ocean`
  gains the offsets its file states, and `uddf/legacy-writer` keeps a reading at `30.4 s`
  that it lost to the one at `30 s`. No fixture is added or retired.

- **A recording carries its device's readouts and its salinity setting (§3, §6.2, §6.4a).**
  `surface_pressure`, `cns_start`, `cns_end`, `otu_start` and `otu_end` sat on the dive, where
  a dive worn on two computers has two answers to each and the format could hold one — the
  argument §6.4a already made for `mode`. And the dive's `water_type` offered `en13319`,
  which is a computer's calibration rather than a kind of water, and could say nothing of a
  second computer set differently. The five move to §6.4a with their constraints unchanged,
  and §3's rule 4 counts a readout among what makes a recording, since a CNS figure a diver
  copied off their computer is a record nothing else can produce. The recording gains
  `salinity` — `fresh`, `en13319` or `salt` — and `water_type` keeps `salt`, `fresh` and
  `brackish`; a reader derives neither from the other. `mode`, `deco_model` and `salinity`
  still do not make a recording, and a water density in kg/m³ is deliberately not here: it
  is a different member from a named setting, and arrives in a minor version when a reader
  maps one. `docs/converting.md` gains the rule for a readout a source states on the dive —
  the primary recording takes it, reported `resolved` where there are two.

  **This is a breaking change and it lands inside 1.0**, on the same ground as the ones
  below. It breaks documents: a readout on a dive is an undefined member now, and
  `"water_type": "en13319"` fails the enum. `fixtures/invalid/` gains
  `dive-readout-outside-recording`, the retired shape, and `water-type-en13319`, the value
  the enum no longer holds. Every other `invalid/` document moved its readouts onto its
  primary recording with the valid corpus, so each keeps its one defect;
  `dive-profile-outside-recording` has no recording to take them and drops them.
  `valid/two-computers` carries a readout set on each of its recordings, and they differ, and
  `valid/technical-dive` a `salinity` of `en13319` on a dive in salt water. A recording of
  readouts alone is in both corpora: `valid/technical-dive`'s third dive carries a `cns_end`
  and nothing else, and `ssrf/trip-grouping`'s third dive gains an `@cns` and an `@otu` that
  arrive on a recording of their own.

- **A dive's start may be a date (§5.2, §6.2, §6.4a).** `started_at` was a REQUIRED
  date-time, so a source that recorded the day and not the time — a bare UDDF `<datetime>`,
  Subsurface's `2002-06-18T`, a `.ssrf` dive with no `@time` — left a converter midnight,
  which is §5.4's fabrication and reads back as a dive that began at midnight. A dive's
  `started_at` may now be a full-date: readers MUST NOT place such a dive at any time of day
  or show a clock for it, and MUST preserve it as a date. A recording's `started_at` stays a
  date-time, and a recording that states none on such a dive has an axis whose origin is the
  day. §5.2's naming rule names `started_at` as the one member holding either kind.
  `docs/uddf-writing.md` writes the bare date, which UDDF's documentation spells and its XSD
  refuses, and says why.

  **This is a breaking change and it lands inside 1.0**, on the same ground as the ones
  below. It breaks readers rather than documents: every document that validated still does,
  while a reader written against an earlier draft may parse a dive's start as a date-time
  and meet one that is not. `valid/technical-dive` gains a dive logged with its day alone. No
  `invalid/` file is added: a malformed start fails the schema's patterns, the rejection
  `trailing-newline-datetime` already pins for a date-time.

- **`notes` has no length limit (§6, §9).** Seven record types capped a note at 10 000
  characters, a figure with no ground in the format — the free text a converter reads from
  every other format is unbounded — so a converter truncated a longer note and reported the
  rest dropped, and a cap cannot rise in a minor version once readers size storage to it.
  `$defs/notes` loses its `maxLength`, the seven rows say nothing about length, and §9 says
  notes of any length on **seven** record types, where it said six. The other bounded
  strings keep their bounds: each is a name, a number, a label or an identifier, short by
  what it is, where a note is prose. Those that were unbounded stay so.

  **This is a breaking change and it lands inside 1.0**, on the same ground as the ones
  below. It breaks readers rather than documents: a reader that sized its storage at 10 000
  meets a longer note. No fixture is added or retired.

- **§6.16's agency vocabulary is widened, for the last time (§6.16, §6.17).** It is a
  REQUIRED vocabulary and freezes at the tag (§7), and the seed missed agencies with real
  card holders — a freediving agency among them — each of which would have been `"other"` for
  the life of 1.x. It gains `ndl`, `utd`, `saa`, `scotsac`, `iac`, `protec`, `pdic`, `nase`,
  `sei`, `ymca`, `erdi`, `aida`, `molchanovs`, `pfi`, `apnea_academy`, `fii`, `nss_cds`,
  `nacd`, `idea` and `diwa`, each an agency that issues or issued cards; `pdic` and `ymca`
  issue none now and name cards a logbook still holds. §6.17's course shares the list. The
  "seeded wide" sentence stays and now says the vocabulary takes no further values: after
  the tag an agency not on it is `"other"`.

  **This is a breaking change and it lands inside 1.0**, on the same ground as the ones
  below. It breaks readers rather than documents: a reader written against an earlier draft
  treats a value it does not know as absent (§5.6), which a REQUIRED member cannot survive.
  `valid/technical-dive` carries an `aida` card.

- **A cylinder's `po2_limit` is `ppo2_limit` (§6.3).** The planned ceiling, the profile's
  `ppo2` channel and the `ppo2_high` event are one quantity, and the ceiling alone spelled it
  another way. The member is renamed in the schema, in the five mapping rows that write it
  and in every fixture that carries it; `docs/uddf-writing.md` names only `<maximumpo2>`.

  **This is a breaking change and it lands inside 1.0**, on the same ground as the ones
  below. It breaks documents: `po2_limit` is an undefined member, which the schema rejects
  and `fixtures/invalid/undefined-member.divejson` already names, so no invalid fixture is
  added.

- **The order of `format` and `version` is a SHOULD (§3, §4).** Writers had to emit
  `format` first and `version` second, and a document whose members came in another order
  failed validation — while the reader §5.5 asks to preserve extensions it did not
  understand is a generic re-serialisation, and in two mainstream ecosystems the default one
  sorts keys: Go's `encoding/json` sorts a map's, and Rust's `serde_json` keeps a sorted map
  unless its `preserve_order` feature is on. Nothing dispatches on the first bytes of a JSON
  file. §4 says SHOULD, and §3's list loses the rule, so its rule 7 is rule 6.

  **This is a breaking change and it lands inside 1.0**, on the same ground as the ones
  below. It breaks readers rather than documents: every document that validated still does.
  `fixtures/invalid/version-not-second.divejson` and `version-before-format.divejson`
  retire, since an `invalid/` file must fail and nothing fails either now.

- **The `divejson` producer key is reserved (§3, §5.5).** A converter following
  `docs/converting.md` writes its source's provenance and its `inferred` list under
  `extensions.divejson`, while §5.5 reserved nothing, so a 1.0 producer could lawfully have
  taken the key and a later reservation would have broken it. It is reserved now, and a
  writer that does not follow that document MUST NOT use it. It is a writer-behaviour rule of
  §5.4's kind, and §3 lists it with them: a document carrying the key is conforming when such
  a converter wrote it, so nothing in a document shows a violation, and no fixture and no
  validator rule accompany it.

  **This is a breaking change and it lands inside 1.0**, on the same ground as the ones
  below. It breaks no document; a writer that put its own members under the key moves them.

- **A diver carries a portrait, and a member holding a Stored File ends `_file` (§5.2, §6.1,
  §6.7, §9).** `portrait_file` is one optional Stored File on the Diver: a photograph that
  identifies the diver to another person, the picture as the diver supplied it, whole, since
  each reader crops it to its own frame. §6.1's rule on what an import applies only once the
  importing diver confirms it names the portrait beside the four check-in facts, §6.7 and
  §9's archives bullet list it beside card scans, and §5.2 states the naming every Stored
  File member already follows — `_file`, and `_files` for an array — with no exceptions. The
  member is additive, so it lands inside 1.0 with `$id`, `title` and `version` untouched.
  `technical-dive` carries one on both sides of its UDDF write pair, and `fixtures/invalid/`
  gains `duplicate-file-uuid-portrait`, a portrait sharing a card side's uuid, which §5.3
  forbids and the schema cannot see.

  **UDDF has no home for it** in either direction: `<owner>` has no image, and the images a
  `<notes><link>` reaches carry no role, so `docs/uddf-mapping.md` reads none of them as a
  portrait and `docs/uddf-writing.md` reports the member dropped.

- **A diver carries a phone, a date of birth, emergency contacts and insurances, and the
  Diver's own strings are bounded (§6.1, §9).** The four are what a dive desk asks a diver
  for, and they shipped under the `opendiving` producer key before arriving here, the path
  §5.5 describes into the core. `phone` is one free-text number and `born_on` a date;
  `emergency_contacts` and `insurances` are arrays of two new objects, the contacts in the
  order they are to be called. An **Emergency Contact** requires a `name` and an
  **Insurance** a `provider`, so a phone with nobody beside it, or a number with no insurer,
  never travels. §6.1's rule that a document never overwrites an account's identity or
  settings now names what those are, and a reader SHOULD NOT apply the four new members
  without the importing diver confirming them; §9's dossier gains them, an emergency
  contact being another person's data.

  **The members are additive and the bounds are a tightening**: `name` ≤ 255, `username` ≤
  64 and `email` ≤ 255, the person-facing strings the schema had left unbounded. A minor
  version could not tighten a constraint (§7); the untagged draft can, so this lands inside
  1.0 with `$id`, `title` and `version` untouched. `fixtures/invalid/` gains
  `diver-name-too-long`, `diver-username-too-long` and `diver-email-too-long` for the
  tightening, and `emergency-contact-without-name` and `insurance-without-provider` for the
  two new REQUIRED members.

  **UDDF has a home for three of the four.** `docs/uddf-mapping.md` and
  `docs/uddf-writing.md` map `born_on` to `<birthdate>`, `phone` to `<contact><phone>` and
  each insurance to a `<diveinsurances><insurance>`, a date written as a `<datetime>` at
  midnight, and report `emergency_contacts` and an insurance's `number`, which have none. An
  owner that records any of them and no name is a diver in both directions:
  `owner-profile-only` is that pair each way, and the `opendiving` and `technical-dive`
  pairs carry the rest.

- **A dive site's `location` is the object a trip part's already was (§6.9, §6.10).** The
  format said where things are in two ways: a trip part carried a structured place with a
  position and a geocoded extent, while a dive site carried a free-text locality. Both
  members were spelled `location`, both were filled from the same lookup, and one of them
  kept a composed label and threw away everything else the lookup returned. §6.9's **Trip
  Location** is now **Location** and both hosts reference it, so a reader that can frame a
  map on a trip's place can frame one on a site's. §3's `south ≤ north` rule names both
  hosts, §5.3's list of objects with no independent identity says "locations", and §6.10
  gains the prose that keeps a site's two positions apart: `position` is the site's own
  pin, `location.position` is the locality's centre, and neither may be filled from the
  other. `docs/uddf-mapping.md`'s two place tables now read into one object, and
  `docs/uddf-writing.md` records what a site's locality costs on the way out — its
  `<geography><location>` holds the name, so the full name, the centre and the box are
  reported dropped where a part loses only its box.

  **The two text members are `name` and `full_name`**, where they were `name` and
  `display_name`. `name` is the place as a person writes it — `"Moalboal"` typed,
  `"Dahab, Egypt"` looked up — and `full_name` is the fullest written form the source held
  for it. The old member is removed rather than re-pointed: it meant the fuller form, which
  is what `full_name` now holds, and it is named after the one word geocoders disagree
  about — Nominatim's `display_name` is the long string where Google Places' `displayName`
  is the short one. Nothing binds the two to each other, and §6.9 says so as an observation
  rather than as a rule: `full_name` is usually the longer and is not required to contain
  `name`.

  **This is a breaking change and it lands inside 1.0**, on the same ground as the ones
  below: the draft's status line lets normative text, schema and fixtures change together
  until the tag, and nothing is tagged. `$id`, `title` and `version` are untouched at `1.0`.
  It breaks documents as well as readers — a `sites[].location` string is no longer of the
  declared type, and `display_name` is an undefined member that every definition being
  `additionalProperties: false` rejects outside `extensions`. An exporter that has not moved
  fails loudly rather than filing a postal chain where readers expect a place name.
  `fixtures/invalid/` gains `site-bbox-south-exceeds-north.divejson`: the box rule has two
  hosts now, and a validator that walks only trips passes the trip-hosted file perfectly.

- **A trip is a sequence of parts (§6.8, §6.9a), and it carries no dates of its own.** A
  trip was one date range beside an ordered list of undated places, which models a week in
  one place and nothing else: the two shapes divers actually log — a liveaboard week and
  then a hotel week, a drive down a coast stopping in three towns — both collapsed into one
  span with a list of names next to it, and the file could not say which dives happened
  where. §6.9a's **Trip Part** is the stretch that carries its own `starts_on`, its own
  `ends_on` and its own `location`; §6.8's `locations` becomes `parts`, `starts_on` and
  `ends_on` come off the trip, and a trip's span is the earliest `starts_on` among its parts
  and the latest `ends_on`. §6.9's Location is what a part's `location` holds. §3's
  `ends_on ≥ starts_on` rule moves from the trip to the part, and §5.3's list of objects
  with no independent identity gains the part.

  **A trip may now have no dates at all.** Each of a part's dates is independently optional,
  as a course's are, so a trip whose parts carry none has no span — and that is why
  `starts_on` is dropped rather than moved down still REQUIRED. A place the diver recorded
  and never dated is a record, and a transit day is a part with dates and no place.

  **This is a breaking change and it lands inside 1.0**, on the same ground as the ones
  below: the draft's status line lets normative text, schema and fixtures change together
  until the tag, and nothing is tagged. `$id`, `title` and `version` are untouched at `1.0`.
  It breaks documents as well as readers — `trips[].locations`, `trips[].starts_on` and
  `trips[].ends_on` are undefined members now, and every definition being
  `additionalProperties: false`, the schema rejects each. `fixtures/invalid/trip-dates-reversed.divejson`
  puts its reversed range on a part and the three `bbox-*` files hang their box off
  `parts[].location`, so no invalid fixture is added and none retires.

  **UDDF is where the gap was loudest, and it closes.** `<trippart>` was already a stretch
  with its own dates and its own place, so `docs/uddf-mapping.md` stops folding a file's
  per-part dates into one span and `docs/uddf-writing.md` stops putting a trip's whole span
  on the first part it emits. `fixtures/write/uddf/technical-dive.uddf` is the pair that
  shows it: three `<trippart>`s where there were two, and each of the three shapes §6.9a
  allows.

- **A course's `agency` is OPTIONAL (§6.17).** A course a private instructor taught has no
  agency, and a REQUIRED member left a writer inventing one — the failure §5.4 exists to
  forbid, and §5.4's own test says a course is interpretable from its name. §6.16's
  certification `agency` stays REQUIRED: a card is the artefact an agency issued, so a
  certification naming none is not a poorer record but a different claim. §6.17 now states
  the vocabulary freeze in its own words, because §7 grants new enum values in OPTIONAL
  members and an inherited licence would let a course's agencies drift from the
  certification's — the one thing sharing that vocabulary exists to prevent.

  **This is a breaking change and it lands inside 1.0**, on the same ground as the ones
  below: the draft's status line lets normative text, schema and fixtures change together
  until the tag, and nothing is tagged. `$id`, `title` and `version` are untouched at `1.0`.
  It breaks readers rather than documents — every document that validated still does, while
  a reader written against an earlier draft may take a course's `agency` for granted and now
  meets one without it. `agency_other` without an `agency` stays invalid, which the pairing
  conditional already gave for free and `fixtures/invalid/course-agency-other-without-agency.divejson`
  now holds it to.

- **A dive's number is `number`, a certification's is `number` (§6.2, §6.16), and §5.2
  states the rule those two were the only members breaking: a member is never prefixed with
  the name of the object that carries it.** The prefix is a flat-table habit nested JSON
  does not need, and on the dive it collided with a different fact: §6.4b's `dive_number` is
  a device's own count of the dives it recorded, not the diver's numbering, and every
  sentence about either had to name a section to say which one it meant. The names tell them
  apart now, so those sentences say it in the member. The device keeps `dive_number` — it is
  prefixed with *another* object's name, which the rule permits, and it is the only
  `dive_number` left in the format.

  **This is a breaking change and it lands inside 1.0**, on the same ground as the ones
  below: the draft's status line lets normative text, schema and fixtures change together
  until the tag, and nothing is tagged. `$id`, `title` and `version` are untouched at `1.0`.
  A document written against an earlier draft carries `dive_number` on its dives and
  `certification_number` on its certifications, both undefined members now: the schema
  rejects each, every definition being `additionalProperties: false`, and a reader that
  meets one ignores it (§5.6). That failure is the one
  `fixtures/invalid/undefined-member.divejson` already names, so no invalid fixture is added
  and none retires.

- **A recording carries its mode and its deco model (§6.4a, §6.4c), and a profile carries
  the decompression readouts (§6.4).** What a dive computer *computes* is a class of data
  the format had no room for, and none of it survives the dive: the recording gains `mode`
  — `open_circuit`, `closed_circuit`, `semi_closed`, `gauge` or `freedive` — and
  `deco_model`, a new object holding the algorithm family, the device's own name for the
  model, a Bühlmann gradient-factor pair and the device's conservatism setting; the profile
  gains six channels, `ndl` and `tts` in seconds, `ppo2` in hundredths of a bar, `cns` in
  tenths of a percent, and `gradient_factor` and `surface_gradient_factor` in whole percent.
  Both sit on the recording rather than on the dive, because two computers on one dive run
  two models and show two clocks, which is why divers wear two. §5.1 gains the scales, §3
  gains the `gf_low ≤ gf_high` rule the schema cannot express, and the schema gains a series
  definition whose values are floored at zero — every one of the six is a quantity with no
  negative reading, so a source's negative is its absent-marker rather than a value.

  **A freedive is a dive now.** `converting.md`'s *not a scuba dive* rule covered two things
  under one sentence — a record that is no dive at all, which is still skipped, and a
  freedive, which was dropped whole for want of a member saying what kind of dive it was.
  There is a member. `fixtures/suunto_xml/freedive.xml` converted to a conforming logbook
  with no dives in it and now converts to the dive it always was.

- **An event's `type` is OPTIONAL, and `other` is gone (§6.6).** This is the breaking half.
  §7 forbids adding values to a REQUIRED member's vocabulary, so a REQUIRED `type` would
  freeze the event vocabulary at the 1.0 tag and every alarm a computer records — a ceiling
  violation, a fast ascent, a ppO₂ alarm — would be `other` with a label for the life of
  1.x. Absent `type` now means unclassified and makes `label` REQUIRED, which is exactly
  what `other` meant, so `other` goes rather than stand as a second spelling of it (§5.4).
  The vocabulary is seeded from what real alarms name: `ascent_rate`,
  `safety_stop_mandatory`, `safety_stop_violation`, `deep_stop_violation`,
  `ceiling_violation`, `ndl_reached`, `ppo2_high`, `pressure_low` and `depth_alarm`, beside
  the existing `gas_switch`, `deep_stop`, `safety_stop` and `bookmark`. §7 gains a rule that
  a value defined after 1.0 travels with a `label`, so a 1.0 reader meeting one treats the
  type as absent (§5.6) and still has a labelled marker at the right second.

  **This is a breaking change and it lands inside 1.0**, on the same ground as the one
  below: the draft's status line lets normative text, schema and fixtures change together
  until the tag, and nothing is tagged. A document written against an earlier draft may
  carry `"type": "other"`, which the schema now rejects; the same event with its `label` and
  no `type` is the conforming spelling. `fixtures/invalid/event-other-without-label.divejson`
  retires — `other` is no longer a type it can fail on — and two files replace it:
  `event-without-type-or-label.divejson` and `deco-model-gf-order.divejson`.

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
- The corpus adopts the four pairs the first implementation carried ahead of it, and CI
  returns to a released pin — `divejson==0.5.0`, which is the chore that closes the order
  `CONTRIBUTING.md` opens for a change to what validates. Three of the four are one dive
  read three ways: a Suunto Ocean's own FIT recording, the app's JSON of the same
  recording, and Subsurface's save of it beside a second computer's, whose two
  `<divecomputer>` elements both carry samples and so become two recordings with two
  profiles — the first element supplying the dive's own depths and temperature, the second
  its own start 32 s later, and the `Serial` and `FW Version` `<extradata>` a device's
  serial and firmware. The fourth is the corpus's first Shearwater Cloud Desktop export, so
  `docs/uddf-mapping.md`'s generator rule — a `Z` read as the local wall clock it is — is
  held to a file this repository carries rather than to files it does not.
- `docs/uddf-writing.md` gains the two round-trip findings a UDDF writer reports and that
  document described neither of. A dive that links a `computer` gear item no recording's
  device matches sends its profile and its device counter back on **that** machine, because
  a reader takes both off the first `<divecomputer>` the dive links while the links run in
  the kit list's order with the device elements appended after; and a dive whose own
  computers are reached in another order gets its recordings back reordered, which §6.4a
  makes a fact about the document rather than a presentation detail. What is *gained* — a
  linked computer no recording answers to — stays unreported, nothing being lost by it.
