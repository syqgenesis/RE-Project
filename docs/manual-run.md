# Manual run: the whole workflow by hand

The manual run does three jobs at once:

1. **Learn the workflow.** Every stage of the pipeline (spec §4) done by hand and timed, so we see
   where the time and the hard judgement calls actually are.
2. **Build the gold set.** The packets and labels you make here are what the model is scored
   against (spec §6).
3. **Test the model with zero code.** Paste each packet into a model chat and score its answers.

Rough effort (estimates; replace with measured times after the pilot): gathering ~25 min per
packet, judging ~8 min per property. Phase 1 comes to about **12–15 h each** across the two
founders.

---

## Setup (once, ~30 min)

1. **Google Sheet** with three tabs, each imported from the CSV headers in `eval/`:
   - `properties`: which set each property is in (**judges shouldn't look at this column**).
   - `labels`: one row per property per labeller (A, B, consensus, baseline, model).
   - `friction`: every time something is slow, missing or ambiguous.
2. **Shared Drive folder** `runs/`, with one subfolder per property: `runs/CAM-001/` etc. Images
   are too heavy for git; keep packets in Drive.
3. Agree labeller IDs (`A`, `B`) and read `docs/rubric.md` together once.
4. Tools: desktop browser (Google Maps' measure tool needs desktop), a screenshot tool that can draw
   a red outline, and Google Earth Pro or Earth web for historical imagery (backtest set only).

---

## Phase 0: Pilot (5 properties, ~half a day each)

Pick 5 live listings with a mix: 2 ordinary terraces or semis, 2 detached or corner, 1 marketed
"with potential". **Both** of you do Parts A and B on **all 5**, independently, and time every step.
Then:

- Compare packets. Did you pin the same address and get the same measurements? Where did they
  differ, and why?
- Compare labels (see *Reconcile* below).
- Revise `docs/rubric.md` and `templates/packet.md`, bump the version, and add a changelog line.
- Write up the **top 5 friction points**. This is the start of the build backlog.

Pilot properties are **not** part of the gold set, because the rubric was tuned on them.

---

## Phase 1: Gold set (40 properties)

### Choosing properties → `properties` tab

| Set | n | How |
|---|---|---|
| `random` | 25 | On Rightmove, search each of CB1…CB5 in turn: houses + bungalows, **exclude** under offer / sold STC. Note the result count per district and allocate the 25 roughly in proportion. Pick positions with `=RANDBETWEEN(1, count)` on a "newest listed" sort. |
| `marketed` | 8 | Listings in CB1–CB5 whose text mentions development potential, a plot, or planning. Use the portal's keyword filter where available, or search `site:rightmove.co.uk "development potential" Cambridge`. Exclude land-only listings. |
| `backtest` | 7 | In the [Greater Cambridge planning portal](https://applications.greatercambridgeplanning.org/online-applications/search.do?action=advanced), search descriptions for *"erection of" dwelling* and *"land rear of"* / *"land adjacent to"*, decided 2021–2024, CB1–CB5. Take **5 granted** and **2 refused** where the new house would sit in an existing garden. The **as-of date** is ~1 month before the application date. |

Give each property an ID (`CAM-001`…), **shuffle the order** so sets are mixed, and split
gathering 20/20.

**Archive every live listing immediately:** Print → Save as PDF, and download the floorplan and
photos. Listings vanish when they sell.

### Part A: gather the packet (one person, ~20–30 min)

Copy `templates/packet.md` to `runs/<id>/packet.md` and fill it in. Log minutes per step in
`friction`.

**A1. Listing facts (~5 min).** Copy price, type, tenure, beds, floor area and EPC rating, and paste
the description verbatim.

**A2. Pin the exact address (~5 min).** Portals usually hide the house number. Tricks, best first:
- Search the [EPC register](https://find-energy-certificate.service.gov.uk/) by postcode, then match
  the listing's EPC score (e.g. "68 D") and floor area.
- Match listing photos (front door, windows, car port) against Street View along the street.
- Fall back on the listing's map pin (often only approximate).

Record *how* you pinned it. Address resolution is one of the hardest things to automate.

**A3. Imagery (~5 min).** Google Maps → Satellite, **north up, scale bar visible**:
- `sat_close.png`: the plot plus ~2 neighbours each side filling the frame.
- `sat_context.png`: the whole block, ~150–250 m across, including the houses behind.
- `streetview_front.png`: front of the house, framed to show both side gaps.
- Outline the subject plot **in red** on both satellite shots. Otherwise the model doesn't know
  which house you mean.
- *Backtest:* use Google Earth historical imagery and Street View's "See more dates" to get images
  **before the as-of date**. Current imagery may show the new house.

**A4. Measure (~5 min)** → packet §6 only. In Google Maps, right-click → *Measure distance*:
- Rear garden depth: rear wall of the main house to the back fence, perpendicular.
- Frontage width, and the side gaps between the house and each side boundary.
- Plot area: click around the boundary back to the start point, and the total area appears.
- Measure 3 neighbouring plots' areas for "typical neighbour plot".
- Note uncertainty, e.g. a boundary hidden under trees.

**A5. Constraints (~5 min)** → packet §3. Record what you searched and where:
- [greatercambridgeplanning.org](https://www.greatercambridgeplanning.org/): postcode lookup shows
  conservation areas, TPOs and flood zones.
- [Historic England list](https://historicengland.org.uk/listing/the-list/): is the house, or its
  neighbour, listed?
- [planning.data.gov.uk map](https://www.planning.data.gov.uk/map/): Article 4 directions, Green Belt.
- [EA Flood Map for Planning](https://flood-map-for-planning.service.gov.uk/): confirm the flood zone.

**A6. Planning history (~5–10 min)** → packet §4.
[Greater Cambridge public access](https://applications.greatercambridgeplanning.org/online-applications/):
- Search the subject address first.
- Then the street name: last ~10 years, up to the as-of date.
- Keep only what matters: new dwellings, backland, big extensions, and **all refusals**.
- *Backtest:* leave out the target application itself.

**A7. Comps (~5–10 min)** → packet §5.
- Sold prices from [HMLR price paid](https://landregistry.data.gov.uk/app/ppd) (or a portal's
  sold-prices page, which uses the same data): same street, then ~500 m; last 36 months; same type.
  Aim for 5, minimum 3.
- Floor area for each comp from the EPC register. Compute £/m².
- Mark whether each comp is visibly extended on satellite. Extended vs unextended comps on the same
  street show what extending is worth.
- Fill in the median, asking £/m² and the % difference.

**A8. Sufficiency check (1 min).** Could someone who has never seen this house make the call from
the packet alone? If you leaned on anything that isn't in it, add it and log it in `friction`.

### Part B: judge (both founders, independently, ~5–10 min each)

- Judge **from the packet only**, using `docs/rubric.md`.
- **Don't** look at the other person's row, the `properties` tab, or any model output until both
  rows are in.
- Fill the observation fields first, then the score. Record your judging minutes.
- For `rear_garden_depth_m` and `plot_area_m2`, give your own estimate from the images. Don't copy
  packet §6. Those columns measure how well people (and the model) can eyeball size.

### Reconcile (together, ~2–5 min per property)

For each property, compare A and B. Discuss it if the **shortlist call differs** or the **scores
differ by ≥ 2**. Then:

- Write a `consensus` row (every property gets one, even when A and B agree).
- In `notes`, tag the cause of each disagreement:
  - `rubric-ambiguous` → fix the rubric (only allowed during the pilot; see freeze below).
  - `packet-missing-info` → fix the packet.
  - `genuine-judgement` → leave it.
- Before moving on, check the **pre-gate** (spec §6.3): κ ≥ 0.6 and within-1 ≥ 80%.

**Freeze.** Once Phase 1 labelling starts, the rubric, thresholds and keyword list are frozen. If
you must change the rubric, re-judge everything it affects.

---

## Phase 2: Model run (~3 min per property)

Follow `prompts/site-assessment-v0.md`:
- A fresh chat for each property, the same model throughout. Record the model name in `labeller`.
- Send the prompt, then the rubric, then packet §0–5 with the images attached. **Never send §6.**
- **First answer counts.** No regenerating or nudging. If it's malformed, record it as-is (that's
  a G1 fail, and worth knowing).
- Paste its CSV row into `labels` as `model:<name>:full`.

**Keyword baseline (B0).** In `labels`, add a `baseline:keywords` row per property:
`shortlist` = Y if the packet description matches the spec §6.2 phrase list. In Sheets:
`=IF(REGEXMATCH(LOWER(desc), "development potential|development opportunity|building plot|planning permission|subject to planning|stpp|potential to extend|scope to extend|large plot|generous plot|substantial plot|double plot|corner plot|large garden|backland"),"Y","N")`

---

## Phase 3: Score

Compute these in the sheet (spec §6.7 has the definitions):

1. **Pre-gate:** A vs B κ and within-1.
2. **G1–G3:** check every model row. For **G2**, open each shortlisted card plus 10 random ones and
   verify every comp, planning ref and address it cites against the packet.
3. **G4–G7:** model vs consensus, and B0 vs consensus for G6.
4. **Diagnostics D1–D8.** For D1/D2 compare against packet §6 and consensus. For D4 use the
   backtest planning outcomes and refusal reasons.
5. Read off the **verdict** (spec §6.6) and write a half-page summary: what passed, what failed, and
   the top 5 friction points.

---

## Friction log: what to capture

One row per snag: `property_id, who, step (A1–A8, B, C), minutes, what was slow/missing/ambiguous,
automation idea`. Examples of what's worth logging:
- "Couldn't find the house number."
- "Rear boundary hidden by trees."
- "Planning search by street returned 200 results."
- "Needed the side elevation, which wasn't in the packet."

After the pilot and after Phase 1, sort by total minutes. That ranking is the build order.
