# Scoring rubric — v0.1

Humans and the model both judge with this rubric, and they judge **from the packet alone**
(`templates/packet.md`). If you needed something that isn't in the packet to decide, add it to
the packet and log it in the friction log. Don't quietly use it.

Numbers marked *(heuristic)* are starting guesses. They aren't planning rules. Tune them in the
pilot, then freeze them.

---

## 1. Opportunity types

| Code | What it means | Typical signals |
|---|---|---|
| `BACKLAND` | New dwelling in the rear garden | Deep rear garden, and vehicle-width side access **or** a road/lane at the back or side |
| `SIDE_INFILL` | New dwelling beside the house (side plot, end of terrace, corner) | Wide gap to the side boundary, corner plot, the street's building line continues into the gap |
| `REPLACEMENT` | Demolish and rebuild larger, or rebuild as 2+ units | Bungalow or small house on a big plot, low site coverage, bigger or denser houses next door |
| `SUBDIVISION` | Split the existing building into more units | Very large house, flats or HMOs already nearby |
| `EXTENSION` | Materially more floor area with no new unit (rear/side, loft, upward) | House unextended while most neighbours have extended; room on the plot |
| `NONE` | Nothing beyond cosmetic work | — |

A property can have a `primary_type` and a `secondary_type`, e.g. `BACKLAND` + `EXTENSION`.

## 2. Observation fields ("look first")

Fill these in **before** scoring. They are what you (or the model) *see*, not your judgement.

| Field | Values | Definition |
|---|---|---|
| `side_access` | Y / N / U | Clear route from the road to the rear garden wide enough for a driveway (≈3.5 m+ *(heuristic)*) |
| `rear_or_side_road_frontage` | Y / N / U | The plot touches a second road or lane at the back or side |
| `corner_plot` | Y / N | Plot sits on a road junction |
| `existing_extension` | Y / N / U | The subject house is already visibly extended (rear/side extension, loft dormer) |
| `significant_trees` | Y / N | Mature trees cover a meaningful part of the likely building area |
| `outbuildings` | Y / N | Garage, workshop, annexe etc. in the garden |
| `rear_garden_depth_m` | number | Rear wall of the main house to the rear boundary, perpendicular, in metres |
| `plot_area_m2` | number | Whole plot, m² |
| `plot_vs_neighbours` | smaller / similar / larger / much_larger | Compared with the typical adjacent plot. `much_larger` = ≥1.5× |
| `neighbours_extended` | none / some / most | Share of the ~5 houses either side with visible extensions or dormers |
| `backland_nearby` | Y / N | Houses built behind the street frontage within the same block / ~200 m |

## 3. Score (1–5)

| Score | Anchor | Would we… |
|---|---|---|
| **5** | **Obvious.** One or more new dwellings clearly fit: corner or double-frontage plot, or a wide side plot, or a plot much larger than the neighbours. Precedent nearby. No major constraints. | Book a viewing today |
| **4** | **Credible.** A new dwelling (or replacement with more units) works on dimensions and access, with no hard constraints. At most one notable risk (conservation area, tight access, a tree). | Do a site visit |
| **3** | **Possible but doubtful.** A new dwelling is conceivable but there is a major doubt: access unclear or narrow, dimensions marginal, a strong constraint. **Or** a big extension well beyond the street norm. | Keep an eye on it |
| **2** | **Minor.** Ordinary extension or loft potential that the rest of the street has already done or could do. Nothing unusual about the plot. | Ignore |
| **1** | **None.** Flat, plot fully built out, or blocked. | Ignore |

**Shortlist = score ≥ 4.** v0 is looking for *new-unit* opportunities. Extension-only plays top out
at 3 by design (open question in the spec §8).

## 4. Hard caps (apply before you finalise the score)

| Condition (from packet) | `blocker` value | Max score |
|---|---|---|
| Flat / maisonette, or no control of the land | `flat` | 1 |
| Plot fully built out (little rear garden, no side gap) | `built_out` | 2 |
| In Green Belt | `green_belt` | 2 |
| Subject building is listed | `listed` | 3 |
| Flood Zone 3 | `flood_zone_3` | 3 |

If several apply, record the one with the lowest cap. Conservation area, TPO and Article 4 don't cap
the score, but if present they **must** appear in the risks.

## 5. Signals *(heuristics)*

**Positive**
- Backland: rear garden ≥ ~30 m deep **and** (`side_access` = Y **or** rear/side road frontage).
  Roughly: garden kept for the existing house + a new house + its garden.
- Side infill: ≥ ~6 m gap to the side boundary on a detached, end-of-terrace or corner house, and a
  new house there would keep the street's building line.
- Plot `much_larger` than neighbours.
- Low site coverage: house footprint under ~15% of the plot.
- **Precedent**, the strongest signal: an approved new dwelling or backland house within ~200 m in
  the last ~10 years, or backland houses visible on the same block.
- Unextended house on a street where `neighbours_extended` = most (extension upside, and proof the
  planners accept it).

**Negative**
- Uniform terraced street with no rear lane (backland access is almost never possible).
- Only route to the rear would remove the existing house's parking or squeeze past windows.
- Mature trees over the likely building area (TPO or ecology risk).
- Neighbours' rear windows close to where a new house would go (overlooking).
- Refused applications for similar schemes nearby.

## 6. Prices

- **Comps:** sold prices from the packet only. Same street first, then ~500 m, last 36 months,
  same type (detached/semi/terrace).
- **£/m²** = price ÷ EPC floor area. `price_position` compares the asking £/m² with the comps' median:
  `below` (< −10%), `at` (±10%), `above` (> +10%), `unknown`.
  `above` can mean the potential is already priced in, so say so in the risks.
- **`uplift_band`**: rough *gross* value of what would be added (new dwelling or extra floor area ×
  comps £/m²). Build costs are ignored in v0.

| Band | Gross value added | Typical of |
|---|---|---|
| `S` | < £150k | Extension |
| `M` | £150k–£400k | Big extension / small dwelling |
| `L` | £400k–£800k | One new house |
| `XL` | > £800k | Multiple units |
| `NA` | — | Score 1–2 |

## 7. Confidence

- `high`: you'd be surprised to be wrong.
- `med`: the call rests on one uncertain fact.
- `low`: key facts are unknown (boundary unclear, access unclear, images poor).

## 8. Output fields (one row per property per labeller)

Same columns as `eval/labels.csv`.

| Field | Values |
|---|---|
| `property_id` | e.g. `CAM-001` |
| `labeller` | `A`, `B`, `consensus`, `baseline:keywords`, or `model:<name>:<mode>` |
| `date` | YYYY-MM-DD |
| `minutes` | time spent judging (not gathering) |
| observation fields | see §2 |
| `blocker` | none / flat / built_out / green_belt / listed / flood_zone_3 |
| `price_position` | below / at / above / unknown |
| `primary_type`, `secondary_type` | codes from §1 (`secondary_type` may be `NONE`) |
| `score` | 1–5 |
| `shortlist` | Y / N (must equal `score ≥ 4`) |
| `uplift_band` | S / M / L / XL / NA |
| `confidence` | low / med / high |
| `reason_1..3` | one line each, **ending with its evidence tag**, e.g. `[sat_close]`, `[planning:23/01234/FUL]`, `[comps]` |
| `risk_1..2` | one line each, with an evidence tag |
| `change_my_mind` | the single fact that would most change the score |
| `notes` | free text |

Evidence tags: `[listing]` `[floorplan]` `[sat_close]` `[sat_context]` `[streetview]`
`[constraints]` `[planning:<ref>]` `[comps]` `[measurements]`.

---

### Changelog
- v0.1 (2026-09-26): first draft, before the pilot.
