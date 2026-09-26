# v0 spec: Cambridge development-potential screener

Status: **draft v0.1**, 2026-09-26. Thresholds get frozen at the end of Phase 1 (§7).

## 1. What v0 is

For every house for sale in Cambridge, produce a **Site Card** answering three questions: does this
plot have development potential, what kind, and why. The card draws on the listing, satellite and
Street View imagery, the neighbours, planning history and sold prices. The cards are then ranked into
a shortlist worth a site visit.

v0 is an **experiment, not a product**. It answers two questions:

1. Given the same packet of information a human uses, **does the model make the same shortlist call
   we do?**
2. **Does the satellite imagery add signal** beyond the listing text? If a keyword filter on
   "development potential" does as well, the imagery isn't earning its keep.

Real-world practicality (scraping, API terms, licensing, costs) is deliberately out of scope (§9).

## 2. Scope

| | In | Out |
|---|---|---|
| Area | Cambridge city: postcode districts **CB1–CB5** | Villages (CB21–CB25), for now |
| Stock | Houses and bungalows for sale, freehold | Flats, land-only plots, under offer / sold STC |
| Opportunity | New units: `BACKLAND`, `SIDE_INFILL`, `REPLACEMENT`, `SUBDIVISION`. `EXTENSION` is recorded but can't reach the shortlist | Commercial, change of use, auctions |
| Economics | Rough gross value added (band), asking £/m² vs comps | Build costs, finance, full residual appraisal |

## 3. Definitions

Opportunity types, observation fields, the 1–5 score, hard caps and the shortlist rule
(**score ≥ 4**) all live in [`rubric.md`](rubric.md). It is the single source of truth for humans
and the model.

## 4. Pipeline (target design)

Division of labour: **code fetches facts and does geometry, the model does perception and judgement,
code enforces hard caps.** In the v0 test a human does every "code" step by hand
([`manual-run.md`](manual-run.md)).

| # | Stage | Output | Target owner | Manual v0 source |
|---|---|---|---|---|
| 1 | Listing intake | Price, type, beds, floor area, description, photos, floorplan | code | Rightmove / Zoopla / OnTheMarket |
| 2 | Resolve address | Full address, postcode, lat/lon | code | Listing map pin + EPC register match + Street View |
| 3 | Imagery | `sat_close`, `sat_context`, `streetview_front` | code | Google Maps satellite + Street View |
| 4 | Geometry | Plot area, garden depth, frontage, side gaps | code (HMLR INSPIRE polygons + building outlines); model estimate as fallback | Google Maps measure tool |
| 5 | Constraints | Conservation area, listed, Article 4, TPO, flood zone, Green Belt | code | greatercambridgeplanning.org postcode lookup, planning.data.gov.uk, Historic England list, EA flood map |
| 6 | Planning history | Relevant applications on the subject and the street | code (fetch) + model (relevance) | Greater Cambridge planning public access |
| 7 | Comps | Sold prices, EPC floor areas, £/m² | code | HMLR Price Paid + EPC register |
| 8 | **Perception** | Observation fields (rubric §2) | **model** | Human, from images |
| 9 | **Judgement** | Type, score, reasons, risks, band, confidence | **model** | Human, with rubric |
| 10 | Caps and ranking | Final score, shortlist | code | Rubric §4 |

## 5. Inputs and outputs

- **Input: packet** ([`templates/packet.md`](../templates/packet.md)). Listing facts, 3–6 images,
  constraints table, planning history table, comps table. Section 6 holds human measurements
  (gold) and is **withheld from the model** in end-to-end mode.
- **Output: Site Card.** One row with the fields in rubric §8 / [`eval/labels.csv`](../eval/labels.csv).
  The model also returns the same data as JSON ([`prompts/site-assessment-v0.md`](../prompts/site-assessment-v0.md)).

## 6. Evaluation

### 6.1 Gold set (n = 40)

| Set | n | How chosen | Ground truth |
|---|---|---|---|
| `random` | 25 | Random live listings across CB1–CB5, roughly proportional to stock per district | Human consensus |
| `marketed` | 8 | Live listings whose text mentions development potential, plot or planning | Human consensus |
| `backtest` | 7 | Garden plots where a new dwelling was **granted (5)** or **refused (2)** in 2021–24. Packet built "as of" before the application (historical imagery) | Consensus, plus the actual planning outcome |

Labelling protocol:
- Each packet is gathered **once**. Both founders then judge **all 40 independently** from the packets.
- Where they disagree, they reconcile into a `consensus` row.
- **Blinding:** the set name never appears in a packet. Backtest packets exclude the target
  application and anything dated after the as-of date.

### 6.2 Systems compared

| System | What it is |
|---|---|
| `A`, `B` | Each founder, independently |
| `consensus` | Reconciled label. The yardstick for everything below |
| `baseline:keywords` (B0) | Shortlist = listing text contains any of: *development potential, development opportunity, building plot, planning permission, subject to planning, STPP, potential to extend, scope to extend, large plot, generous plot, substantial plot, double plot, corner plot, large garden, backland* (case-insensitive). List frozen now |
| `model:<name>:full` | Model, end-to-end: packet sections 0–5 plus images, no human measurements |
| *(code phase)* `model:<name>:oracle` | Same, plus packet §6 measurements. Isolates judgement from perception |
| *(code phase)* `model:<name>:notext` | Same as `full` minus the listing description. Isolates what the images contribute |

### 6.3 Pre-gate: can humans agree?

Before judging the model, check the humans agree with each other:
- A vs B shortlist **Cohen's κ ≥ 0.6**, and
- A vs B score within ±1 on **≥ 80%** of properties.

If either fails, **stop**: the rubric is too ambiguous to measure a model against. Fix the rubric
and re-judge. The model can't be held to a bar the humans don't clear.

### 6.4 Pass/fail criteria (gating)

`model:<name>:full` against `consensus`, all 40 properties. **All must pass.**

| ID | Criterion | Threshold | Why |
|---|---|---|---|
| G1 | Valid output | 100% of cards parse and use allowed values; `shortlist` = (score ≥ 4) | Can't automate what we can't parse |
| G2 | No fabrication | **0** invented comps, planning refs, addresses, or sourced-looking facts not in the packet. Checked on every shortlisted card + 10 random | One invented comp destroys trust |
| G3 | Caps respected | **0** cards scored above their rubric §4 cap | Never shortlist a flat or Green Belt plot |
| G4 | Shortlist recall | **≥ 0.80** (with ~12 positives: miss ≤ 2) | A screener's main job is not to miss deals |
| G5 | Shortlist precision | **≥ 0.50** (at most half the shortlist is noise) | Keeps site-visit time sane |
| G6 | Beats keyword baseline | F1(model) − F1(B0) **≥ 0.10** | Otherwise the imagery adds nothing |
| G7 | Score agreement | \|model − consensus\| ≤ 1 on **≥ 80%** | Calibration, not just the binary call |

### 6.5 Diagnostics (tracked, not gating)

| ID | Metric | Target | Tells us |
|---|---|---|---|
| D1 | Accuracy on Y/N observation fields | ≥ 85% | Can it *see* access, corners, extensions, trees? |
| D2 | Median absolute % error, `rear_garden_depth_m` and `plot_area_m2` | ≤ 20% | If it fails, move geometry to code (expected) |
| D3 | `primary_type` match, where consensus score ≥ 3 | ≥ 70% | Right kind of opportunity? |
| D4 | Backtest: granted sites shortlisted; refused sites have the planners' main refusal reason in the risks | ≥ 4/5; ≥ 1/2 | Agreement with real planning outcomes, not just our opinion |
| D5 | Reason usefulness on shortlisted cards (humans rate 0 wrong / 1 partly / 2 useful) | mean ≥ 1.5 | Would we act on the explanation? |
| D6 | `uplift_band` match | ≥ 60% | Is the price step sensible? |
| D7 | `price_position` match | ≥ 90% | It's arithmetic; if it misses, move it to code |
| D8 | Minutes per property: gather / human judge / model | Record | Where the time goes, and the value of automating |
| D9 | *(code phase)* Consistency: 3 runs per property, score range ≤ 1 | ≥ 90% | Is the output stable? |
| D10 | *(code phase)* `oracle` vs `full` F1; `notext` vs `full` F1 | Record | Perception vs judgement error; value of imagery |

### 6.6 Verdict

| Verdict | Rule | Next step |
|---|---|---|
| 🟢 **GREEN** | Pre-gate passes, G1–G7 all pass | Build v1: automate stages 1–7 and 10 |
| 🟡 **AMBER** | G1–G3 pass, some of G4–G7 fail | Diagnose with D1/D2 (perception) vs D3/D5 (judgement). Fix inputs or prompt once, then confirm on **≥ 10 freshly labelled listings**, not the same 40 |
| 🔴 **RED** | G2 or G3 still fail after one fix, **or** G6 fails | Rethink: the model is unreliable or the imagery adds nothing |

### 6.7 Metric definitions

- Positive = `shortlist` = Y (score ≥ 4). Precision = TP/(TP+FP), recall = TP/(TP+FN),
  F1 = 2PR/(P+R), all against `consensus`.
- Cohen's κ = (p_o − p_e)/(1 − p_e) on the binary shortlist, A vs B.
- Within-1 = share of properties where \|score_x − score_y\| ≤ 1.

### 6.8 Caveats

- **Small n.** With ~12 positives, each miss moves recall ~8 points. Read the results as
  directional, not statistically tight.
- **Freeze before the model run.** Thresholds, rubric and keyword list are frozen at the end of
  Phase 1. Any change after the model has run requires a fresh confirmation set (§6.6).
- **Leakage.** Current imagery can show the new house on backtest sites. Use historical imagery
  dated before the application. Listing text in the `marketed` set is real-world signal, which is
  exactly why B0 exists.
- **Gatherer bias.** The founder who gathered a packet has seen more than the packet. Judge only
  from what's in it.

## 7. Phases

| Phase | What | Exit criterion |
|---|---|---|
| 0. Pilot | 5 properties. Both founders do everything independently, including gathering | Rubric and packet template revised; per-step times known |
| 1. Gold set | 40 packets (split gathering), both judge all 40, reconcile | Pre-gate (§6.3) passes. **Freeze rubric v1 and thresholds** |
| 2. Manual model run | Paste each packet into a fresh model chat; score B0 in the sheet | 40 model rows recorded |
| 3. Score | Compute §6.4–6.5 | Verdict (§6.6) |
| 4. Build | Only on GREEN or AMBER: automate, then run D9/D10 | — |

## 8. Open questions (decide before Phase 1)

1. Should big `EXTENSION` plays be able to reach the shortlist? (Currently capped at 3.)
2. Stay in CB1–CB5, or add the necklace villages (more plots, more Green Belt)?
3. Is there a price ceiling for what we'd actually consider?
4. Which model and version to freeze for Phase 2? Record it in every model row.

## 9. Deferred: real-world practicality (noted, not solved)

Portal scraping terms (Rightmove et al.), Google Maps Platform terms for storing and analysing
imagery, restrictive covenants and title (HMLR title register), highways and fire access standards,
ecology and biodiversity net gain, CIL/S106, local plan policy on garden development, build-cost
appraisal.
