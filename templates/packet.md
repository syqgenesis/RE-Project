# Packet: <property_id>

> Copy to `runs/<property_id>/packet.md`. Everything in sections 0–5 is what the judges and the
> model see. Section 6 is gold and is **not** given to the model in `full` mode.
> Don't write the set name (random / marketed / backtest) anywhere in this file.

## 0. Admin
- property_id:
- as-of date: <!-- today for live listings; for backtest, a date before the target application -->
- listing URL:
- archived as: `listing.pdf`

## 1. Listing facts
- Address (full, incl. number):
- How the address was pinned: <!-- e.g. EPC register match on postcode + floor area + rating -->
- Postcode:
- Asking price: £
- Property type: detached / semi / terrace / end-terrace / bungalow
- Tenure:
- Beds / baths:
- Floor area: m² (source: EPC / floorplan)
- EPC rating:
- Listing description (paste verbatim):

```
```

## 2. Images (files in this folder)
Rules: north up, scale bar visible, **subject plot outlined in red**.

| File | What | Captured |
|---|---|---|
| `sat_close.png` | Subject plot + ~2 neighbours each side | date shown on imagery, if any |
| `sat_context.png` | Whole block, ~150–250 m across, incl. houses behind | |
| `streetview_front.png` | Front of house, showing side gaps | Street View date |
| `floorplan.png` | From listing | |
| `photo_garden_*.png` | Up to 3 listing photos of the garden / rear | |

## 3. Constraints
| Constraint | Y / N / Unknown | Source (site + what you searched) |
|---|---|---|
| Conservation area | | |
| Listed building (subject) | | |
| Listed building adjacent | | |
| Article 4 direction | | |
| Tree Preservation Order on/next to plot | | |
| Flood zone (1 / 2 / 3) | | |
| Green Belt | | |

## 4. Planning history (subject + street, last ~10 years, up to the as-of date)
Only relevant applications: new dwellings, backland, large extensions, and any refusals.

| Ref | Address | Description (short) | Decision | Date |
|---|---|---|---|---|
| | | | | |

## 5. Sold-price comps (up to the as-of date)
Same street first, then ~500 m; last 36 months; same type. Aim for 5, minimum 3.

| Address | Date sold | Price £ | Type | Floor area m² (EPC) | £/m² | Visibly extended? |
|---|---|---|---|---|---|---|
| | | | | | | |

- Median comps £/m²:
- Asking £/m² (asking ÷ floor area):
- Difference: %

---

## 6. Measurements (GOLD, withheld from the model in `full` mode)
Measured with Google Maps right-click → *Measure distance*.

| Measure | Value | Notes / uncertainty |
|---|---|---|
| Rear garden depth (rear wall → rear boundary) | m | |
| Plot width at frontage | m | |
| Side gap, left (house → boundary) | m | |
| Side gap, right | m | |
| Plot area | m² | |
| Typical neighbour plot area (3 measured) | m² | |
