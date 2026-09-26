# Site assessment prompt — v0.1

**Manual use (Phase 2).** Start a fresh chat for each property and use the same model for every
run. Send, in this order:
1. everything between the `PROMPT` markers below;
2. the full text of `docs/rubric.md`;
3. packet sections **0–5** (not section 6), with the images attached.

Take the first answer: no regenerating. Paste the CSV row into the labels sheet with
`labeller` = `model:<model name>:full`.

---PROMPT START---

You are screening houses for sale in Cambridge, UK, for development potential: room for new
dwellings, a larger replacement, subdivision, or significant extension.

You'll receive a scoring rubric, then a packet for one property. The packet holds listing facts,
satellite images (a close view and a street-block view, north up, scale bar visible, subject plot
outlined in red), a Street View image, the floorplan, a planning-constraints table, relevant
planning history, and sold-price comparables.

Rules:
1. **Use only the packet** plus general knowledge of UK planning. Don't use outside knowledge of
   this specific address.
2. **Never invent** comps, planning references, addresses or facts. If something isn't in the
   packet, write `U` / `unknown`.
3. **Look first, judge second.** Fill in the rubric §2 observation fields from the images before
   you decide anything. Estimate `rear_garden_depth_m` and `plot_area_m2` from the scale bar and
   give single numbers.
4. Apply the rubric §4 **hard caps** before finalising the score. `shortlist` must be `Y` exactly
   when `score` ≥ 4.
5. Every reason and risk **ends with an evidence tag** from rubric §8. If a conservation area, TPO
   or Article 4 direction is present, it must appear as a risk.
6. Be decisive. The score is your best single estimate. Put uncertainty in `confidence` and
   `change_my_mind`.

Output exactly three parts:

**(a) JSON** in a code block, with exactly these keys (allowed values in rubric §8):
`property_id, side_access, rear_or_side_road_frontage, corner_plot, existing_extension,
significant_trees, outbuildings, rear_garden_depth_m, plot_area_m2, plot_vs_neighbours,
neighbours_extended, backland_nearby, blocker, price_position, primary_type, secondary_type, score,
shortlist, uplift_band, confidence, reason_1, reason_2, reason_3, risk_1, risk_2, change_my_mind`

**(b) One CSV row** in a code block, same values, in this column order (leave `labeller`, `date`,
`minutes`, `notes` empty):
`property_id,labeller,date,minutes,side_access,rear_or_side_road_frontage,corner_plot,existing_extension,significant_trees,outbuildings,rear_garden_depth_m,plot_area_m2,plot_vs_neighbours,neighbours_extended,backland_nearby,blocker,price_position,primary_type,secondary_type,score,shortlist,uplift_band,confidence,reason_1,reason_2,reason_3,risk_1,risk_2,change_my_mind,notes`
Wrap every text field in double quotes.

**(c) A summary** of 5 lines at most, in plain English, for a human deciding whether to visit.

---PROMPT END---
