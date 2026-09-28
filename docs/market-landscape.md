# Market landscape: UK residential flipping

Status: first draft, 2026-09-28. A map for customer discovery. Names are examples to look up, not
endorsements, and a few are from web search only, so check them before relying on them.

## 1. The market in numbers

- **~10,570 homes flipped in England & Wales in 2025**: 1.5% of all sales, the lowest share in over
  a decade (down from 21,560 in 2016). "Flipped" here means bought and resold within 12 months
  ([Hamptons](https://www.hamptons.co.uk/articles/lowest-share-of-homes-flipped-in-a-decade)).
- **Average gross profit after stamp duty: ~£16,400** in 2025, down 55% from £36,500 in 2015. After
  stamp duty only ~59% of flips made a gross profit
  ([Mortgage Solutions](https://www.mortgagesolutions.co.uk/mortgage-news/2026/04/13/house-flipping-falls-to-low-as-property-taxes-eat-into-profits-hamptons/)).
- **Why:** the stamp duty surcharge on additional homes rose from 3% to 5% in 2024.

What this means for us:
- Cosmetic "buy low, paint, sell" flips are getting squeezed. Flippers need a **bigger value-add per
  deal**: extensions, conversions, planning gain. That's what the tool detects.
- It's also a shrinking pool, so which flipper type we serve first matters.
- Planning-gain deals often take longer than 12 months, so Hamptons' number undercounts them.

## 2. Types of flipper (the tool serves all of them)

| Type | What they do | Typical hold | Signal the tool must detect |
|---|---|---|---|
| Cosmetic | Kitchen, bathroom, decoration | 3–6 months | Condition (dated photos), asking price vs comps |
| Heavy refurb | Rewire, replumb, structural fixes | 6–12 months | Condition, "in need of modernisation", probate / auction |
| Extension | Loft, rear or side extension, then sell | 6–12 months | `EXTENSION`: room on plot, `neighbours_extended` = most |
| Conversion | House → flats or HMO (shared house) | 9–18 months | `SUBDIVISION`: large house, flats nearby |
| **Planning gain** | Get planning for a new home in the garden; sell house + plot, or build | 12–24 months | `BACKLAND`, `SIDE_INFILL` |
| Replacement | Demolish and rebuild bigger or as 2+ homes | 18–30 months | `REPLACEMENT`: bungalow on a big plot |

Note: `docs/rubric.md` currently caps extension-only plays at 3, so they never reach the shortlist.
To serve cosmetic, refurb and extension flippers, the rubric needs condition signals and a separate
shortlist per flip type.

**Interview slice (first):** planning-gain flippers. See §4.

## 3. Who the players are, stage by stage

### Find: where deals come from
| Category | Examples |
|---|---|
| Property portals | Rightmove, Zoopla, OnTheMarket |
| Cambridge estate agents | Bidwells, Cheffins, Savills, Carter Jonas, Hockeys, Pocock+Shaw, Redmayne Arnold & Harris |
| Auctions | Cheffins (Cambridge), Allsop, Savills Auctions, Auction House, iamsold |
| Plot marketplaces | PlotBrowser (~300 Cambridgeshire plots), Plotfinder, Savills building plots |
| Deal sourcers | Individuals and small firms selling deals for a 2–3% fee |
| Garden-plot buyers | GardensandLand (buys garden land from homeowners) |
| Off-market | Letters to homeowners, probate lists, word of mouth |

### Assess: deal-finding and data tools (our competitors)
| Tool | What it's known for |
|---|---|
| **PropertyData** | Investor analytics; scans listings for strategies, including development potential |
| PropertyEngine | Fast filtering of on-market listings |
| Property Filter | Finding motivated sellers |
| Nimbus Maps | Planning history, ownership, development potential |
| LandTech (LandInsight) | Site sourcing for small developers |
| Searchland | Land and site sourcing |
| PaTMa Prospector | Investor deal analysis |
| Realyse | Location and yield data |

Free public data behind most of them: HM Land Registry price paid, the EPC register, Companies
House, council planning portals, planning.data.gov.uk.

### Finance
| Category | Examples |
|---|---|
| Bridging lenders (short-term loans to buy fast) | Together, LendInvest, Precise (OSB Group), Shawbrook, Castle Trust Bank |
| Brokers | Spark Finance and many small brokers. Great informants: they know every active flipper |
| Development finance | Specialist banks (e.g. Shawbrook) for build-out |

### Buy, add value, sell
| Stage | Players |
|---|---|
| Legal | Conveyancing solicitors; title-split specialists |
| Survey / valuation | RICS surveyors |
| Design & planning | Architects, planning consultants, the council planning team |
| Build | Small builders (FMB members) |
| Sell | Estate agents, auctions, plot marketplaces |

### Community, education, media
| Category | Examples |
|---|---|
| Communities & meetups | Property Hub (forum + *The Property Podcast*), Progressive Property (PPN), Property Investors Network (PIN), Property Tribes |
| Trade bodies | RICS (surveyors), Propertymark (agents), FMB (builders), HBF (housebuilders), NRLA (landlords), RTPI (planners) |
| Rules to know | Stamp duty surcharge (5%); anti-money-laundering registration with HMRC and a redress scheme if you sell deals for a fee |
| Trade media | Property Industry Eye, Estates Gazette, Property Week, Landlord Today, Property Investor Today, The Negotiator |

## 4. Finding planning-gain flippers

The fingerprint in public data: **the person who applied for planning bought the house shortly
before applying**, and **the house or plot was sold again after permission**.

1. **Plots for sale with planning.** Every consented garden plot on PlotBrowser, Zoopla or Savills
   was created by someone who got planning. Look up the planning reference; the applicant is often
   the seller.
2. **Planning + price-paid cross-check.** For garden-plot applications, check price-paid data: bought
   less than 2 years before applying = investor, not a long-time homeowner. Resold after permission
   = completed flip.
3. **Companies House.** SIC code 68100 ("buying and selling of own real estate") is literally the
   flipper's code. Filter to Cambridge; companies named after a street are usually single-deal
   companies.
4. **Bridging brokers.** Ask them: "Who have you funded for a buy-and-get-planning deal in
   Cambridge?"
5. **Communities.** Speakers at PIN and PPN who talk about "title splits" or "garden plots"; threads
   on the Property Hub forum.
6. **Architects and planning consultants** who work on garden-plot schemes. Their clients are this
   customer.

### Qualifying questions (every call)
1. How many deals have you done yourself in the last 3 years? (0 → not a customer)
2. Did any involve getting planning for a new home on the plot? (no → a different flipper type; log
   separately)
3. Your own money and decision? (advisers and sourcers → informant)
4. Buying in or around Cambridge? (no → park for later)
