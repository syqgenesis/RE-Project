# UK deal-sourcing, property-data and site-finding tools: competitor map for an on-market "value-add potential" screener

> **Method and reliability note (read first):** Research was done on 2026-09-28. Every vendor, review and news page tried with WebFetch was blocked by the network egress proxy: propertydata.co.uk, searchland.co.uk, land.tech, trustpilot.com, augustapp.com, propdetect.com, sitelens.co.uk, landhunt.io, insidermedia.com and geovation.uk. The session's shared web-search budget then ran out part way through, so the tools in the "Gaps" sections were never searched. **Every finding below comes from search-engine result summaries of the cited URLs. No page was read in full.** Treat exact prices and numbers as "seen in search snippet, 2026-09-28" and re-check them on the vendor page before quoting them externally. Many comparison and "review" pages are written by competitors, for example PropDetect reviewing Property Filter, SiteLens on Nimbus, LandHunt on Searchland, Searchland on LandTech and PropertyData "alternative-to" pages. Those are flagged where used.

## Q1. Competitor map: who each tool is for, core features, pricing, company facts

### Takeaway
The market has two clusters. (a) **Investor deal-sourcing tools** cost about £4–£250/month and run month to month: PropertyData, Property Filter, PropertyEngine, PaTMa, Property Deals Insight, and newer AI entrants PropDetect, PropMarker and PropDealAI. They screen *on-market listings* mostly on price signals such as below-market value (BMV), reductions, fall-throughs and yield. (b) **Land/site-sourcing platforms** cost about £195+/month, usually on annual contracts or quote-only: LandTech/LandInsight, Searchland, Nimbus, Landstack, and cheaper newcomers LandHunt and SiteLens. They focus on *off-market land titles*, ownership, planning and constraints. Few tools bridge the two clusters.

### Cited Findings

#### A. Investor / deal-sourcing tools (on-market focus)

**PropertyData (propertydata.co.uk)**: buy-to-let, HMO and flip investors and sourcers; also markets itself against land tools
- Web app "from £14/month", no monthly commitment, 14-day free trial with all features (as of 2026-09-28, snippet) — [PropertyData pricing](https://propertydata.co.uk/pricing); [Propalt blog](https://propalt.ai/resources/blogs/uk-property-data-api)
- API is credit-based: £28/month for 2,000 credits, £96 for 15,000, £192 for 50,000, up to £1,300 for 500,000. Annual billing is 12 months for the price of 11. Rate limits run from 4 to 24 requests per 10 seconds by tier (as of 2026-09-28, snippet) — [Propalt blog](https://propalt.ai/resources/blogs/uk-property-data-api); [PropertyData API pricing](https://propertydata.co.uk/api/pricing)
- Algorithms scan the market daily against **~40 sourcing strategies**. These include a **"Large plot" strategy** (about 2,056 freehold properties on a large plot were live at the time) and an **"Unbroken freeholds" strategy for possible title splitting** (about 2,555 freeholds containing multiple properties) — [PropertyData source-on-market](https://propertydata.co.uk/source-on-market); [PropertyData features](https://propertydata.co.uk/features)
- There is also a "properties near a large development" sourcing strategy — [PropertyData](https://propertydata.co.uk/sourcing/near-large-development)
- The **Plot Map** tool shows title number, plot size, known addresses, planning applications, listed buildings, and recent transactions or listings — [PropertyData Plot Map](https://propertydata.co.uk/videos/plot-map)
- Pulls together Land Registry sold prices, rental comparables, planning data including Article 4 and HMO licensing areas, and yield and demand heat maps. The August blog calls it "the research engine most UK sourcers build their analysis on" — [August blog](https://www.augustapp.com/blog/best-property-sourcing-software)
- Has a Chrome extension that overlays data on portals — [Chrome Web Store](https://chromewebstore.google.com/detail/propertydata-data-info-an/nmgflehpkmokienojjgpbddklnedoonp)
- Publishes "alternative to LandInsight" and "alternative to Nimbus Maps" pages, so it is actively pitching into the land-sourcing segment — [PropertyData vs LandInsight](https://propertydata.co.uk/alternative-to/landinsight); [PropertyData vs Nimbus](https://propertydata.co.uk/alternative-to/nimbus-maps)
- Company size, founding year and funding: not found (see Gaps).

**Property Filter (property-filter.co.uk)**: investors and sourcers, with coaching and community bundled in; Coventry-based
- Three tiers at **£100 / £150 / £250 per month ex-VAT**, or £80 / £120 / £200 per month billed annually. 8-day free trial, no contract (as of 2026-09-28, snippet) — [Property Filter pricing](https://property-filter.co.uk/pricing); [PropDetect review (competitor-authored)](https://propdetect.com/compare/property-filter-review)
- Claims 1,800+ members, 10,000+ deals closed over 5 years and 3,250+ accepted offers tracked — [PropDetect review](https://propdetect.com/compare/property-filter-review); [Property Filter](https://property-filter.co.uk/)
- Core idea: consolidates portal listings and adds **motivation signals** (fall-throughs, price reductions, long-listed, relisted, withdrawn), then acts on them with **direct-to-vendor (D2V) letter campaigns**. It also has AI sourcing, deal calculators and comparables — [PropDetect review](https://propdetect.com/compare/property-filter-review); [Property Filter software](https://property-filter.co.uk/software)
- A PropDetect review argues that coaching and community are what justify the £100–£250/month — [PropDetect review](https://propdetect.com/compare/property-filter-review)

**PropertyEngine (propertyengine.co.uk)**: sourcers and deal packagers
- **Starter / Pro / Ultimate** tiers, "start for free", no annual contract. £ figures were not visible in the snippets (see Gaps) — [PropertyEngine pricing](https://propertyengine.co.uk/pricing)
- Starter includes unlimited search, calculators and comparables, but no brochures, no off-market sourcing, limited alerts and no D2V. Pro adds branded reports/brochures and D2V. Ultimate adds an automation platform and 3 Pro seats — [PropertyEngine pricing](https://propertyengine.co.uk/pricing)
- Aggregates Rightmove, Zoopla and other portals, sends real-time alerts "typically within 10 minutes" of listing, and has a built-in sourcing CRM/pipeline — [PropertyEngine sourcing](https://propertyengine.co.uk/features/source-properties); [PropertyEngine features](https://propertyengine.co.uk/features)
- August's comparison: "PropertyData wins on analysis, PropertyEngine on speed, and Property Filter on finding motivated sellers". Most professional sourcers combine a data tool with a deal-finding or pipeline tool — [August blog](https://www.augustapp.com/blog/best-property-sourcing-software)

**PaTMa Property Prospector (patma.co.uk)**: landlords and small investors; also a landlord-management suite
- **Extension Plus £4/month** (£48/year), **Starter £15/month** (£180/year), **Pro £32.50/month** (£390/year). 14-day trial, no card needed, no minimum term (as of 2026-09-28, snippet) — [PaTMa pricing](https://www.patma.co.uk/property-prospector/pricing/)
- Browser extension shows yield, ROI and rent estimates on portals. Price history, yield and ROI are free; addresses and advanced features are paid — [PaTMa Prospector](https://www.patma.co.uk/property-prospector/); [Chrome Web Store](https://chromewebstore.google.com/detail/patma-property-insights/gbppndfkbhfpmpidebmnhkofloklojii)
- **Automated area alerts for new listings, planning applications and sold records.** Can also watch individual properties for price changes, sales, fall-throughs and listing changes — [PaTMa Prospector](https://www.patma.co.uk/property-prospector/)
- Local insights include flood risk and council HMO/licensing information — [PaTMa docs](https://www.patma.co.uk/docs/prospector/features/localdata/)

**Property Deals Insight (propertydealsinsight.com)**: investors, agents, lenders
- Strategy filters for BRR, D2V, HMO, auctions, BMV, repossessions, short lease and discounted properties, plus an "AI-powered Deal Finder". Calculators cover GDV and buy-to-let, and it includes Land Registry price-paid data — [PDI](https://www.propertydealsinsight.com/); [PDI AI deal finder](https://www.propertydealsinsight.com/find-analyse-profitable-property-deals-in-seconds-ai-powered-deal-finder/); [PDI product](https://product.propertydealsinsight.com/)
- Premium Agent package "normally £2,388/year", promoted at £999/year (as of 2026-09-28, snippet) — [PDI](https://www.propertydealsinsight.com/)

**PropDetect (propdetect.com)**: new AI deal analyser for investors
- Watches Rightmove 24/7, runs the full numbers on each match and emails only deals that "stack" ("Deal Radar"). Analysis includes **refurb costed room by room**, valuation from sold comparables, BTL, serviced-accommodation and social-housing rents, and **7 exit scenarios modelled in parallel** — [PropDetect](https://propdetect.com/)
- **Basic £7.99/month (10 analyses), Professional £50/month (100), Enterprise £120/month (500)** (as of 2026-09-28, snippet) — [PropDetect pricing](https://propdetect.com/pricing)

**PropMarker (propmarker.co.uk)**: investors and property trainers
- AI advisor "Lenah" combines listings, sold prices, EPCs and land/planning data. **It reads floorplans to identify extra-bedroom, HMO and conversion potential**, and scores deals by ROI and yield. It also targets BMV, probate and auction stock — [PropMarker](https://propmarker.co.uk/); [AI for PropTech listing](https://aiforproptech.com/companies/propmarker/)
- Claims data on 900k+ live listings, 16M sold records, 34M EPCs and 200M land/planning datapoints. 7-day free trial; £10 single reports via UK Property Reports. Subscription £ figures were not visible — [AI for PropTech](https://aiforproptech.com/companies/propmarker/); [PropMarker pricing](https://propmarker.co.uk/pricing.php)

**PropDealAI (propdealai.com)**: BRRR, HMO and flip investors
- Analyses 1,000+ listings a day and scores each 1–100 across cashflow, equity (asking vs local sold prices) and exit speed (days on market, reductions). Uses the "70% rule" for flips. 7-day trial; price not found — [PropDealAI](https://propdealai.com/)

**Housemetric (housemetric.co.uk)**: investors and buyers; price-per-square-metre research
- Combines Land Registry sold prices with floor area to give **£/m²** for England & Wales. The heat map can **zoom to freehold boundaries of individual properties** — [Housemetric](https://housemetric.co.uk/)
- Premium costs £14.99 for a one-off month or £10/month recurring. The core is free, and the site describes itself as "publicly available data mashed together" — [HouseCheckup comparison](https://housecheckup.co.uk/compare/housemetric); [Housemetric FAQ](https://housemetric.co.uk/faq)

**Sourcing CRMs**
- No product called "Sourcing Buddy" was found; searches returned only the US IDX/CRM product "Buying Buddy" ($49/month) — [Buying Buddy](https://buyingbuddy.com/pricing.php)
- UK sourcers are advised to use generic CRMs such as HubSpot, Pipedrive, GoHighLevel, Zoho and Capsule — [PropSourcer](https://www.propsourcer.com/sourcing-growth-column/5-crm-tools-that-help-property-sourcers-close-more-deals)
- PropertyEngine and Property Filter now bundle CRM/pipeline features — [PropertyEngine](https://propertyengine.co.uk/features/source-properties)

#### B. Data platforms and enterprise data vendors (adjacent; mostly B2B)

**Chimnie**: API covering 35M+ UK properties for insurers, lenders and property service providers
- Founded 2019 by ex-Google data scientist Jon Francis; HQ Bourne. Raised ~$1.7M, last round Nov 2022 from 27 investors — [PitchBook](https://pitchbook.com/profiles/company/515704-96); [Crunchbase](https://www.crunchbase.com/organization/chimnie)
- Combines Ordnance Survey data with hundreds of datasets, "**enriched by AI computer vision** and linking models" — [OS partner page](https://www.ordnancesurvey.co.uk/customers/businesses/find-a-business-partner/chimnie); [Chimnie](https://www.chimnie.com/)

**Sprift**: property reports for agents and conveyancing
- Founded 2016 by Matt Gilpin, a buy-to-let landlord. Seed round Feb 2021 from Second Century Ventures. About 41 employees; London HQ — [Sprift about](https://sprift.com/about-us); [Crunchbase](https://www.crunchbase.com/organization/sprift); [Tracxn](https://tracxn.com/d/companies/sprift/__o_vk3IyIoQlWY7wL0SvJfbmUOxzCw4Zd_wDnQObMfDg)
- Data includes sold prices, flood risk, council tax, conservation areas, leasehold, **plot size, floor area, title plan and planning history** — [Crunchbase](https://www.crunchbase.com/organization/sprift)
- Getlatka lists "$4M revenue"; this is an unverified self-reported or estimated figure — [Getlatka](https://getlatka.com/companies/sprift.com#funding)

**REalyse**: residential market analytics for developers, lenders, investors and consultants
- Aggregates listings, planning, demographics and land ownership — [CB Insights](https://www.cbinsights.com/company/realyse)
- £500k seed in 2017, led by Rajiv Nathwani (Quivira Capital), with Round Hill Capital, Pi Labs and Anthemis — [UKTN](https://www.uktech.news/news/proptech-startup-realyse-closes-500000-seed-20170223)
- Total raised about $4.52M; latest (unattributed) round June 2022; investors include XTX Markets and Growth Lending — [CB Insights financials](https://www.cbinsights.com/company/realyse/financials); [Tracxn](https://tracxn.com/d/companies/realyse/__rRB3EhHa3i5LNrGPYwPtzMRpCd5ODxUhkM4MXeTT8os)

**Kamma**: property licensing and compliance data (HMO, selective licensing) plus climate data
- Customers are mortgage lenders, letting agents and surveyors. Claims 36M properties and 4,000+ users — [UKTN](https://www.uktech.news/proptech/kamma-funding-20230822)
- £3.6M round in Aug 2023 led by Clean Growth Fund, with Triple Point, Pi Labs, Conduit EIS Impact Fund and Kiilto Ventures; £1.6M in 2020 led by Triple Point — [UKTN](https://www.uktech.news/proptech/kamma-funding-20230822); [Clean Growth Fund](https://www.cleangrowthfund.com/news/cgf-leads-3-6m-investment-in-kamma-to-tackle-net-zero-in-uk-property/); [Tech.eu](https://tech.eu/2023/08/21/kamma-ps36m-for-geospatial-tech/)

**Homedata**: UK property data API with a free tier; its site publishes an API price comparison — [Homedata pricing](https://homedata.co.uk/pricing); [Homedata guide](https://homedata.co.uk/guides/best-uk-property-data-api)

#### C. Land / site-sourcing platforms (off-market land focus)

**LandTech (LandInsight, LandEnhance)**: developers, land agents, planners, architects; enterprise and SME
- Founded 2014 (Tracxn) with ~144 employees (Tracxn, Aug 2026). HQ is given as London by Tracxn, while EU-Startups called it "Liverpool-based" in 2021, so **the sources conflict** — [Tracxn](https://tracxn.com/d/companies/landtech/__-j8J8WvlbcrBHm-hMus-iIzd6qecd3vJxGvnl5qE0EE); [EU-Startups](https://www.eu-startups.com/2021/10/liverpool-based-landtech-raises-e49-4-million-for-the-international-expansion-of-its-proptech-platform-for-development-site-sourcing/)
- Funding and customer numbers are covered in Q5. The customer count is **"over 5,000 UK developers"** on the current homepage versus "more than 2,000 clients" in the 2021 coverage — [LandTech](https://land.tech/); [EU-Startups](https://www.eu-startups.com/2021/10/liverpool-based-landtech-raises-e49-4-million-for-the-international-expansion-of-its-proptech-platform-for-development-site-sourcing/)
- Named customers include Taylor Wimpey, CBRE, BNP Paribas, Cushman & Wakefield, JLL and Savills — [EU-Startups](https://www.eu-startups.com/2021/10/liverpool-based-landtech-raises-e49-4-million-for-the-international-expansion-of-its-proptech-platform-for-development-site-sourcing/)
- Pricing has Starter, Pro and Unlimited tiers for LandInsight UK. The £ figures did not render in snippets. US LandInsight starts "from $200/month" — [LandInsight Starter](https://land.tech/pricing/landinsight/starter); [LandInsight US pricing](https://landtech.us/products/landinsight-pricing-plans)
- Searchland claims its top tier is **20% cheaper than LandInsight's** (competitor claim) — [Searchland vs LandTech](https://searchland.co.uk/competitors/searchland-vs-landtech)
- An **AI Assistant** in LandInsight does "instant site triage backed by verifiable source citations" — [LandTech product updates](https://land.tech/blog/topic/product-update)
- **LandEnhance** is a planning-research tool for planners and architects covering England — [LandEnhance](https://land.tech/products/landenhance)
- Acquired Built-ID on 15 Dec 2023 (Tracxn/PitchBook summary) — [Tracxn](https://tracxn.com/d/companies/landtech/__-j8J8WvlbcrBHm-hMus-iIzd6qecd3vJxGvnl5qE0EE)

**Searchland**: land teams, SME developers, architects; also pitched at investors
- Founded 2020 by Mitchell Fasanya (CEO, ex-Fanbytes CTO), Hugh Gibbs (land planner), Arthur Goodhart and Archie Kennedy-Dyson — [Tech.eu](https://tech.eu/2022/11/24/searchland-puts-away-ps23-million/); [Searchland story](https://searchland.co.uk/blog/the-searchland-story-our-backstory-and-how-were-changing-site-sourcing)
- Customer count: "300+ customers in year one", now "1,000 businesses" — [Searchland about](https://searchland.co.uk/about)
- Revenue: Getlatka lists $3.6M in 2023 with a 34-person team (unverified) — [Getlatka](https://getlatka.com/companies/searchland.co.uk)
- **Standard plan from £195 per licence per month billed annually** (1 user), with unlimited searches, planning data, ownership information and **direct-to-owner letter sending**. **Pro** adds strategic land, sales comparables and energy data. **MAX** adds unlimited MCP tokens. Pro and MAX are priced on request, and **all plans have a 12-month minimum** (as of 2026-09-28, snippet) — [Searchland pricing](https://searchland.co.uk/pricing); [SaaSworthy](https://www.saasworthy.com/product/searchland-co/pricing)
- **AI Sourcing Assistant** turns natural-language queries into filters, for example "sites >10 acres, no previous development … within 5 miles of a settlement" — [Searchland blog](https://searchland.co.uk/blog/ai-land-sourcing-assistant); [BestCRE](https://bestcre.com/searchland-ai-review-cre-ai/)
- An **MCP server** lets users plug Searchland data into ChatGPT or Claude — [Searchland pricing](https://searchland.co.uk/pricing); [SaaSworthy](https://www.saasworthy.com/product/searchland-co)
- **Permitted development (PD) search.** The Class MA tool identified 27,599 brownfield sites eligible for commercial-to-residential prior approval — [Searchland PD tool](https://searchland.co.uk/blog/searchland-unveils-new-permitted-development-search-tool)
- Clicking a parcel shows HMLR title boundaries, the corporate ownership tree up to the ultimate parent, and transaction history — [BestCRE](https://bestcre.com/searchland-ai-review-cre-ai/)

**Nimbus Maps (Nimbus Property Systems)**: developers, land and new-homes agents, commercial property
- Co-founded 2015 by brothers Paul and Simon Davis. Based at the University of Warwick Science Park with 60+ staff — [Insider Media](https://www.insidermedia.com/news/midlands/tech-firm-behind-property-mapping-platform-hails-game-changer-funding-package-as-it-looks-to-accelerate-growth)
- Offers off-market site search, ownership, planning history, constraints, "30M+ comparables", and a Brickflow development-finance integration — [Nimbus](https://www.nimbusmaps.co.uk/); [Nimbus dev software](https://www.nimbusmaps.co.uk/property-development-data-software)
- **Plus, Advanced and Enterprise tiers are quote-only**; prices are no longer on its pricing page — [Nimbus pricing](https://www.nimbusmaps.co.uk/pricing-plans); [SiteLens (competitor-authored)](https://sitelens.co.uk/compare/nimbus-maps/)
- Getlatka estimates **$3.4M ARR** and describes the company as bootstrapped (unverified) — [Getlatka](https://getlatka.com/companies/nimbus-maps)

**Landstack**: developers and promoters; Birmingham; founder and MD Jos Pink; member of the Land, Planning and Development Federation (LPDF)
- **Landstack Lite is free**: planning applications, ownership and constraints. **Pro** adds Local Plan policies, land availability assessments, AI features and reporting. Pro price not found — [Landstack plans](https://www.landstack.co.uk/plans/); [Landstack](https://www.landstack.co.uk/); [LPDF](https://www.lpdf.co.uk/members/landstack)

**LandHunt (landhunt.io)**: new; "AI land sourcing that thinks like a planner"; individual sourcers and SME developers
- AI reads planning history, **scores approval odds** and writes the appraisal. Includes ownership, sold prices, viability on one map, and a mobile field app. Its parcel assistant is powered by Anthropic's Claude — [LandHunt](https://landhunt.io/); [LandHunt vs Searchland](https://landhunt.io/vs/searchland)
- Pricing is stated as both "from £19/month" and "from £49/month", no contract (**conflicting figures in snippets**, 2026-09-28) — [LandHunt vs Searchland](https://landhunt.io/vs/searchland)

**SiteLens (sitelens.co.uk)**: planning-application lead generation for subcontractors, trades, suppliers and small developers
- Ingests applications from 380+ councils and classifies them by trade, project type and likely value. Adds Companies House and agent contacts, and sends alerts — [SiteLens](https://sitelens.co.uk/); [SiteLens features](https://sitelens.co.uk/features/)
- Free Explorer tier; **Pro £39/month (£29 annual); Team £99/month (£79 annual)**, up to 5 users (2026-09-28, snippet) — [SiteLens vs Glenigan](https://sitelens.co.uk/compare/glenigan/)
- Registered as SITELENS LTD, company no. 17179769 — [Companies House](https://find-and-update.company-information.service.gov.uk/company/17179769)

**Plot and self-build marketplaces**
- **Plotfinder** costs £5/month online for access to 13,500+ plots and renovation opportunities; the free browse view is limited — [Design for Me comparison](https://designfor-me.com/project-types/self-build/which-plot-finder-website-is-best-for-your-self-build-project/); [Plotfinder subscription](https://subscribe.arcade.plotfinder.net/uk/plotfinder-subscription/dp/c994db54)
- **PlotBrowser** is a free listing of plots — [PlotBrowser](https://www.plotbrowser.com/)
- Both are listings marketplaces, not analytics tools.

**Appraisal tools**
- **Aprao**: London, founded 2017. Covers development feasibility, residual land value and cashflow.
  - SME plan: unlimited projects, 2 feasibilities and 3 users; extra users $119/user/month; 7-day trial — [Aprao SME](https://www.aprao.com/sme-property-developers); [Aprao](https://www.aprao.com/); [Serchen](https://www.serchen.com/company/aprao)

**Free public base layer**
- HMLR INSPIRE Index Polygons show indicative freehold boundaries and are free and updated monthly. They underpin most plot-size tools — [BuyLand](https://buyland.co.uk/blog/inspire-polygons-how-to-see-registered-land-boundaries-for-free); [RoS/HMLR open terms](https://www.ros.gov.uk/about/news/2020/hmlr-and-ros-to-share-inspire-data)

#### D. US analogues (brief)
- PropStream is about $99/month — [BatchData](https://batchdata.io/blog/best-property-data-providers-real-estate-investors)
- DealMachine, Reonomy, TestFit and Up for Growth were not researched because the search budget ran out (see Gaps).

### Inferences
- PropertyData is the incumbent "analysis layer" for UK small investors. Property Filter, PropertyEngine and PaTMa are the "pipeline/alerts layer". A new screener will be compared against the stack users already combine, PropertyData plus one of those. That stack costs about £30–£280/month.
- Searchland and LandTech are the land incumbents. Their price point (£195+/licence/month, 12-month minimum) and off-market land/title workflow suit land teams, not flippers buying a house on Rightmove.
- The 2025–26 entrants (PropDetect, PropMarker, PropDealAI, LandHunt, SiteLens) show AI-native, self-serve, sub-£50 tools are appearing on both sides. The window for a "cheap AI screener" as a differentiator alone is closing, so the differentiator has to be *what* is detected, namely development potential.

### Gaps
- No £ prices were visible for PropertyEngine tiers, LandInsight UK tiers, Nimbus, Landstack Pro, PropMarker or PropDealAI subscriptions. Company size, founding year and funding for PropertyData, Property Filter and PropertyEngine were not found.
- The search budget ran out before these could be researched: **Moverly, August app, Hometrack, TwentyCi, Dataloft, Rightmove/Zoopla data products, LandApp, "Unlock Land", Urbanise, "Resi", PropertyHeads, Planning Portal tools, DealMachine, Reonomy, TestFit and Up for Growth**. Nothing was found under the name "Sourcing Buddy".

## Q2. Pricing ranges, target customer, and feature overlap with the startup's idea

### Takeaway
Monthly pricing splits sharply: **investor tools cost £4–£250/month, month to month**, while **land platforms cost about £195+/licence/month on annual terms or quote-only**. The closest overlaps with the startup are PropertyData (large-plot and title-split screens on listings), PropMarker (floorplan-based conversion potential), PropDetect (refurb costing plus exit modelling on Rightmove listings), and Searchland/LandTech/LandHunt (title, planning and AI triage, but for land).

### Cited Findings
Pricing and terms, all as of 2026-09-28 from search snippets:

| Tool | Target | Price | Terms | Source |
|---|---|---|---|---|
| PaTMa Prospector | Landlords/small investors | £4 / £15 / £32.50 per month | No minimum term | [PaTMa](https://www.patma.co.uk/property-prospector/pricing/) |
| PropDetect | Investors | £7.99 / £50 / £120 per month | Monthly | [PropDetect](https://propdetect.com/pricing) |
| Housemetric | Investors/buyers | Free; £10/month premium | Monthly | [HouseCheckup](https://housecheckup.co.uk/compare/housemetric) |
| Plotfinder | Self-builders | £5/month | Monthly | [Design for Me](https://designfor-me.com/project-types/self-build/which-plot-finder-website-is-best-for-your-self-build-project/) |
| PropertyData | Investors/sourcers (plus land) | From £14/month web; API £28–£1,300/month | No monthly commitment | [PropertyData](https://propertydata.co.uk/pricing); [Propalt](https://propalt.ai/resources/blogs/uk-property-data-api) |
| LandHunt | Sourcers/SME developers | From £19 or £49/month (conflict) | No contract | [LandHunt](https://landhunt.io/vs/searchland) |
| SiteLens | Trades/small developers | Free / £39 / £99 per month | Monthly or annual | [SiteLens](https://sitelens.co.uk/compare/glenigan/) |
| Property Filter | Investors/sourcers (plus coaching) | £100 / £150 / £250 per month ex-VAT | No contract | [Property Filter](https://property-filter.co.uk/pricing) |
| Property Deals Insight | Agents/investors | £2,388/yr list (£999 promo), about £83–£199/month | Annual | [PDI](https://www.propertydealsinsight.com/) |
| Aprao | Developers | Plan-based; extra user $119/month | Trial | [Aprao](https://www.aprao.com/sme-property-developers) |
| Searchland | Land teams/SME developers | From £195/licence/month (annual) | **12-month minimum** | [Searchland](https://searchland.co.uk/pricing) |
| LandInsight | Developers/land teams | UK £ not visible; US from $200/month | Tiers | [LandTech US](https://landtech.us/products/landinsight-pricing-plans) |
| Nimbus Maps | Developers/agents | Quote-only | Sales-led | [Nimbus](https://www.nimbusmaps.co.uk/pricing-plans) |
| Landstack | Developers/promoters | Lite free; Pro on request | n/a | [Landstack](https://www.landstack.co.uk/plans/) |

- SiteLens pitches itself against platforms costing "£5,000/yr on a sales-gated platform" (a competitor's framing of Glenigan and Nimbus-type pricing) — [SiteLens](https://sitelens.co.uk/compare/glenigan/)

Feature overlap with the startup:
- **Listing ingestion and alerts:** PropertyEngine alerts within about 10 minutes — [PropertyEngine](https://propertyengine.co.uk/features/source-properties). PropDetect scans Rightmove daily — [PropDetect](https://propdetect.com/). PaTMa alerts on listings and planning applications — [PaTMa](https://www.patma.co.uk/property-prospector/).
- **Sold-price comps and uplift:** Housemetric gives £/m² — [Housemetric](https://housemetric.co.uk/). PropDetect values from sold comparables — [PropDetect](https://propdetect.com/). PropDealAI compares asking price against local sold prices — [PropDealAI](https://propdealai.com/).
- **Refurb/flip modelling:** PropDetect costs refurb room by room and models 7 exits — [PropDetect](https://propdetect.com/). PropDealAI applies the 70% rule — [PropDealAI](https://propdealai.com/). PDI has a GDV calculator — [PDI](https://www.propertydealsinsight.com/).
- **Plot/title:** PropertyData Plot Map, "Large plot" and "Unbroken freeholds" — [PropertyData](https://propertydata.co.uk/source-on-market). Housemetric shows freehold boundaries — [Housemetric](https://housemetric.co.uk/). Searchland and LandInsight show title boundaries and ownership — [BestCRE](https://bestcre.com/searchland-ai-review-cre-ai/).
- **Conversion potential:** PropMarker reads floorplans for extra bedrooms, HMO and conversion — [PropMarker](https://propmarker.co.uk/).

### Inferences
- There is a pricing "missing middle" between about £50 and £195/month. Tools there would pair (i) self-serve monthly billing like the investor tools with (ii) plot, title and planning intelligence like the land tools. Property Filter sits in that band but earns its price through coaching and community, not development analytics.
- The target customer the startup describes (flippers, small developers, value-add landlords buying *on-market houses*) falls between both clusters. Investor tools model the house as-is or refurbished; land tools model the land and ignore the house.

### Gaps
- No verified per-seat UK price for LandInsight or Nimbus. No usage or churn data for any tool.

## Q3. Which tools already flag "development potential", "title split", "plot size vs neighbours", "extension potential", or listing-keyword alerts

### Takeaway
Explicit flags exist only in coarse form. PropertyData has "Large plot" and "Unbroken freeholds (title split)" strategies on listings. PropMarker has floorplan-based extra-bedroom, HMO and conversion potential. Searchland has PD-rights searches for land and commercial. LandHunt and LandInsight have AI planning triage and approval-odds scoring for land parcels. **No tool found flags per-listing extension potential, garden-plot severability, or plot size relative to neighbours, and none uses aerial imagery on on-market houses.**

### Cited Findings
- **Title split:** PropertyData's "Unbroken freeholds" strategy lists freeholds containing multiple properties "for possible title splitting" (about 2,555 at the time) — [PropertyData](https://propertydata.co.uk/source-on-market)
- **Large plot:** PropertyData's "Large plot" strategy covers freehold properties on a large plot (about 2,056 at the time). The snippet does not say whether "large" is absolute or relative to neighbours — [PropertyData](https://propertydata.co.uk/source-on-market)
- **Plot size / title data:** PropertyData Plot Map shows title number, plot size, planning apps and listed buildings — [PropertyData Plot Map](https://propertydata.co.uk/videos/plot-map). Sprift reports include plot size, floor area, title plan and planning history — [Crunchbase](https://www.crunchbase.com/organization/sprift). Housemetric shows freehold boundaries on its map — [Housemetric](https://housemetric.co.uk/).
- **Conversion, HMO and extra-bedroom potential:** PropMarker AI reads floorplans to identify extra-bedroom, HMO and conversion potential — [PropMarker](https://propmarker.co.uk/)
- **HMO/Article 4 context:** PropertyData shows Article 4 and HMO licensing areas — [August blog](https://www.augustapp.com/blog/best-property-sourcing-software). PaTMa shows local HMO/licensing — [PaTMa docs](https://www.patma.co.uk/docs/prospector/features/localdata/). Kamma provides licensing data to B2B customers — [UKTN](https://www.uktech.news/proptech/kamma-funding-20230822).
- **Permitted development:** Searchland's PD search, including Class MA with 27,599 sites. This targets commercial-to-residential land, not householder extensions — [Searchland](https://searchland.co.uk/blog/searchland-unveils-new-permitted-development-search-tool)
- **Planning-likelihood AI:** LandHunt "scores approval odds" from planning history — [LandHunt](https://landhunt.io/). The LandInsight AI Assistant does site triage with citations — [LandTech](https://land.tech/blog/topic/product-update). LandEnhance does planning research — [LandEnhance](https://land.tech/products/landenhance).
- **Planning-application alerts:** PaTMa sends area alerts for new planning applications — [PaTMa](https://www.patma.co.uk/property-prospector/). SiteLens classifies applications by project type and value across 380+ councils — [SiteLens](https://sitelens.co.uk/).
- **Motivation and listing-change alerts:** Property Filter flags fall-throughs, reductions, long-listed and relisted properties — [PropDetect review](https://propdetect.com/compare/property-filter-review). PaTMa watches individual properties — [PaTMa](https://www.patma.co.uk/property-prospector/).
- **Listing keyword alerts:** PropertyEngine offers "advanced search criteria" with real-time alerts. The snippet did not confirm free-text keyword search such as "potential to extend", "STPP" or "large garden" — [PropertyEngine](https://propertyengine.co.uk/features/source-properties)
- **"Near large development":** PropertyData strategy — [PropertyData](https://propertydata.co.uk/sourcing/near-large-development)

### Inferences
- **No tool was found that computes "extension potential"** (PD envelope such as rear, side or loft vs actual footprint and garden depth) for a listed house. None computes **"plot size vs street/neighbours"** ranking, **severable garden-plot or backland potential** with access/frontage checks, or **"what neighbours got approved"** precedent matching tied to a listing. These are the startup's clearest white space. This rests on search-snippet evidence only, so it is absence of evidence, not proof.
- PropertyData's large-plot and title-split strategies are the nearest incumbent features. PropertyData is also the most likely fast follower, given its data breadth and its pages targeting land-tool alternatives.

### Gaps
- Could not confirm whether any portal (Rightmove or Zoopla) or tool offers saved keyword alerts on listing text; the Rightmove/Zoopla data products were not researched.
- "Resi" (extension/architecture services), PropertyHeads and Planning Portal tools were not researched, so whether any of them has an automated extension-potential estimator is unknown.

## Q4. Reviews on Trustpilot and forums: what users like and complain about

### Takeaway
Users praise PropertyData for data breadth and value, and Property Filter for support and community. Complaints cluster around **billing and trial practices, rate limits and price** (PropertyData), **contracts and renewal pricing** (LandTech), and **review-solicitation concerns** (Trustpilot flagged Property Filter). Forum evidence (Property Tribes, Property Hub, Reddit) could not be read directly.

### Cited Findings
- **PropertyData on Trustpilot** has only about 5 reviews. Complaints: rate limiting unless you buy the top package, seen as too expensive; charged after a free trial despite never receiving account confirmation or being able to log in; 3 months charged without access — [Trustpilot PropertyData](https://www.trustpilot.com/review/propertydata.co.uk)
- **PropertyData** has 343 reviews on Reviews.co.uk, which is its main review platform. Rating not captured — [Reviews.co.uk](https://www.reviews.co.uk/company-reviews/store/propertydata)
- **PropertyData positive quotes** (vendor-curated): "great tool, well worth the money". One user showed a seller local price comparisons and got a lower offer accepted — [PropertyData reviews page](https://propertydata.co.uk/reviews)
- **Property Filter** scores 4.9/5 from about 280 Trustpilot reviews. Praise centres on support ("real people … within 60 seconds"), training and community — [Trustpilot Property Filter](https://uk.trustpilot.com/review/property-filter.co.uk); [PropDetect review](https://propdetect.com/compare/property-filter-review)
- **Trustpilot flagged Property Filter**: it "may be asking for reviews in a way that Trustpilot doesn't support", which can bias ratings — [Trustpilot Property Filter](https://uk.trustpilot.com/review/property-filter.co.uk)
- **Searchland** has about 65 Trustpilot reviews and a 5-star headline rating. Praise covers off-market sourcing, customer service and planning data — [Trustpilot Searchland](https://uk.trustpilot.com/review/searchland.co.uk)
- **LandTech / LandInsight on Trustpilot** is mixed:
  - Praise for patient onboarding of a "technophobe" small developer.
  - A complaint that they "overcharge us then offer us cheaper terms at renewal".
  - [Trustpilot LandTech](https://www.trustpilot.com/review/www.land.tech)
- **PropertyEngine** has a Trustpilot profile (about 12 reviews per the page title); rating and themes not captured — [Trustpilot PropertyEngine](https://ca.trustpilot.com/review/propertyengine.co.uk)
- **Comparison-blog consensus:** "PropertyData wins on analysis, PropertyEngine on speed, and Property Filter on finding motivated sellers". Most pros combine two tools — [August blog](https://www.augustapp.com/blog/best-property-sourcing-software)
- Property Tribes threads on sourcing apps exist, but their content was not retrieved — [Property Tribes: what apps for sourcing](https://www.propertytribes.com/what-apps-do-you-use-for-property-sourcing-t-127646319.html); [Property Tribes: Property Hub for sourcing](https://www.propertytribes.com/using-property-hub-for-deal-sourcing-t-127663010.html)

### Inferences
- Pain points the startup can exploit: (1) price and annual lock-in on land tools; (2) rate and credit limits on data tools; (3) review-trust issues in the coaching-bundled segment. Transparent monthly pricing with no dark patterns on trials is a credible positioning, given the PropertyData billing complaints.
- Review volume is low for most tools (Searchland about 65, PropertyData 5 on Trustpilot). The niche is small and word-of-mouth driven (forums, YouTube and coaching communities), which points to community-led go-to-market.

### Gaps
- Reddit (r/UKProperty, r/HousingUK), Property Hub forum and Property Tribes thread content could not be retrieved, so there are no direct forum quotes. The Reviews.co.uk rating for PropertyData was not captured.

## Q5. Funding rounds and investors

### Takeaway
LandTech is the only heavily funded player: about $61M total, including a €49.4M Series A in Oct 2021 led by Updata Partners. Searchland raised a £2.3M seed (Nov 2022, Fuel Ventures) and **no Series A was found** as of Sept 2026. Most investor-facing tools appear bootstrapped or small. Nimbus has a NatWest IP-backed loan rather than VC. Recent AI entrants are pre-seed or seed; Viability raised £535k.

### Cited Findings
- **LandTech**:
  - €49.4M Series A (Oct 2021) led by Updata Partners, followed by Flashpoint Secondary Fund, with existing investors JLL Spark and Pi Labs — [EU-Startups](https://www.eu-startups.com/2021/10/liverpool-based-landtech-raises-e49-4-million-for-the-international-expansion-of-its-proptech-platform-for-development-site-sourcing/)
  - An earlier €11.2M round; the date was not in the snippet — [Silicon Canals](https://siliconcanals.com/landtech-bags-11-2m/)
  - CIBC Innovation Banking investment (probably venture debt) in March 2024 — [Tracxn](https://tracxn.com/d/companies/landtech/__-j8J8WvlbcrBHm-hMus-iIzd6qecd3vJxGvnl5qE0EE)
  - About $61.2M raised in total — [Tracxn](https://tracxn.com/d/companies/landtech/__-j8J8WvlbcrBHm-hMus-iIzd6qecd3vJxGvnl5qE0EE); [Crunchbase](https://www.crunchbase.com/organization/land-insight)
  - **Nesta participation was not found** in any snippet.
- **Searchland**: £2.3M seed in Nov 2022 led by Fuel Ventures — [UKTN](https://www.uktech.news/proptech/searchland-seed-2m-20221125); [Fuel Ventures](https://www.fuel.ventures/searchland-raises-2-3m-to-help-developers-solve-housing-crisis-with-automation); [Tech.eu](https://tech.eu/2022/11/24/searchland-puts-away-ps23-million/). Search results showed no Series A announcement.
- **Nimbus**: IP-backed loan from NatWest to fund "AI-driven advancements"; amount not captured — [Nimbus blog](https://www.nimbusmaps.co.uk/blog/nimbus-secures-major-funding-from-natwest); [Insider Media](https://www.insidermedia.com/news/midlands/tech-firm-behind-property-mapping-platform-hails-game-changer-funding-package-as-it-looks-to-accelerate-growth). Getlatka calls it bootstrapped with an estimated $3.4M ARR (unverified) — [Getlatka](https://getlatka.com/companies/nimbus-maps)
- **REalyse**: £500k seed (2017), about $4.52M total, latest round June 2022 — [UKTN](https://www.uktech.news/news/proptech-startup-realyse-closes-500000-seed-20170223); [CB Insights](https://www.cbinsights.com/company/realyse/financials)
- **Kamma**: £3.6M (Aug 2023, Clean Growth Fund lead) and £1.6M (2020, Triple Point) — [UKTN](https://www.uktech.news/proptech/kamma-funding-20230822)
- **Chimnie**: about $1.7M, last round Nov 2022 — [PitchBook](https://pitchbook.com/profiles/company/515704-96)
- **Sprift**: seed in Feb 2021 from Second Century Ventures — [Crunchbase](https://www.crunchbase.com/organization/sprift)
- **Viability (formerly Hesti)**: £535k (Sept 2024) from co-founder Paul Higgs, SFC Capital and Clearance Venture Partners, plus HM Land Registry (Geovation accelerator) and Innovate UK grants — [Geovation](https://geovation.uk/insights/viability-secures-535000-in-funding-to-revolutionise-the-housing-market/); [UK Tech News](https://www.uktechnews.info/2024/09/03/viability-secures-535k-investment-from-investors-including-sfc-capital/); [Viability](https://viability.site/2024/09/03/viability-secures-over-500000-in-funding-to-tackle-the-housing-crisis-sustainably/)
- **Aprao**: London, founded 2017; funding not found — [Serchen](https://www.serchen.com/company/aprao)

### Inferences
- Capital in this niche is modest outside LandTech. Searchland reached about 1,000 customers on a £2.3M seed, and Nimbus got to 60+ staff apparently without VC equity. That suggests UK proptech data tools can be capital-efficient, but also that the addressable market may not support large rounds.
- Repeat UK proptech investors appearing across these companies include Pi Labs (LandTech, REalyse, Kamma), Triple Point, Fuel Ventures, SFC Capital, HMLR/Geovation grants and Innovate UK. These are plausible early backers for the startup.

### Gaps
- LandTech's latest valuation, revenue and 2024–26 rounds beyond the CIBC facility. The Nimbus loan amount. Funding for PropertyData, Property Filter, PropertyEngine and PaTMa. Any 2025–26 Searchland round (none found).

## Q6. Startups (2023–2026) using AI or satellite/aerial imagery for garden plots, backland or extension potential in the UK

### Takeaway
The only UK startup found that explicitly combines AI with high-resolution aerial imagery for SME housing developers is **Viability (formerly Hesti)**. It focuses on site viability and offsite construction, not screening on-market houses. The other AI entrants (LandHunt, PropMarker, PropDetect, PropDealAI, and the Searchland and LandInsight AI assistants) work on text, planning and listing data, not imagery. Government AI planning tools and garden-mapping research show the building blocks now exist.

### Cited Findings
- **Viability/Hesti** is an AI platform using **Bluesky high-resolution aerial imagery** and geospatial data for SME home developers to "assess site viability, optimise opportunities" and support offsite construction — [Bluesky](https://bluesky-world.com/2024/12/05/high-resolution-aerial-imagery-from-bluesky-applied-in-revolutionary-new-ai-tool-launched-to-support-uk-housing-developers/); [AGI](https://www.agi.org.uk/bluesky-hi-res-imagery-used-in-new-ai-tool-for-housing-developers/); [Geovation](https://geovation.uk/insights/viability-secures-535000-in-funding-to-revolutionise-the-housing-market/)
  - It **tried satellite imagery first but found the quality insufficient**, then switched to aerial imagery for better resolution and accuracy — [Bluesky](https://bluesky-world.com/2024/12/05/high-resolution-aerial-imagery-from-bluesky-applied-in-revolutionary-new-ai-tool-launched-to-support-uk-housing-developers/)
- **Garden-level segmentation is feasible at national scale.** The RHS and Gentian used ultra-high-resolution satellite imagery and machine learning to map **25.8M gardens in Great Britain** (959,800 ha, 4.6% of land area) — [Countryside Jobs / RHS](https://www.countryside-jobs.com/article/first-ever-ai-mapping-of-uks-growing-spaces-reveals-disparity-in-access-as-rhs-calls-for-greater-provision-of-gardens)
- **Chimnie** enriches property data with "AI computer vision", aimed at insurers and lenders, not development potential — [OS partner page](https://www.ordnancesurvey.co.uk/customers/businesses/find-a-business-partner/chimnie)
- **Government AI:**
  - MHCLG's **Extract** converts historic planning documents, maps and handwritten records into structured data. It has been trialled in 20+ planning authorities and saves about 255 hours per council per year — [GOV.UK](https://www.gov.uk/government/news/ai-tool-to-slash-planning-decision-times-as-government-accelerates-push-to-build-15-million-homes); [PBC Today](https://www.pbctoday.co.uk/news/planning-construction-news/government-launches-planning-upgrade-extract-ai-tool/152120)
  - A prototype supporting **householder decisions** (extensions, conservatories, lofts; about 70% of officer workload) is being tested in Barnet, Camden and Dorset (June 2026) — [MHCLG Digital blog](https://mhclgdigital.blog.gov.uk/2026/06/19/using-ai-to-support-planning-decisions-what-it-means-for-planners-and-residents/)
  - Google DeepMind is collaborating on AI-accelerated planning — [DeepMind](https://deepmind.google/blog/unlocking-uk-house-building-with-ai-accelerated-planning/)
- **AI text and data entrants (no imagery):**
  - LandHunt: approval-odds scoring built on Claude — [LandHunt](https://landhunt.io/)
  - PropMarker: floorplan reading — [PropMarker](https://propmarker.co.uk/)
  - PropDetect: room-by-room refurb costing — [PropDetect](https://propdetect.com/)
  - PropDealAI: 1–100 deal score — [PropDealAI](https://propdealai.com/)
  - Searchland: natural-language AI assistant plus MCP — [Searchland](https://searchland.co.uk/blog/ai-land-sourcing-assistant)
  - LandInsight: AI Assistant with citations — [LandTech](https://land.tech/blog/topic/product-update)

### Inferences
- Viability's experience is a technical warning for the startup. Satellite imagery may be too coarse for garden and extension footprint analysis; aerial imagery from Bluesky or Getmapping, or OS MasterMap building footprints, may be needed, which has licensing cost implications.
- Extract-style structured planning data is spreading across councils. Householder-application precedent data ("which neighbours extended, and how far") should get cheaper and more complete, which lowers the startup's data costs. It also lowers the barrier for PropertyData, Searchland and LandHunt to add the same feature.
- No startup was found doing "on-market house → AI-scored extension, garden-plot or replacement potential". The closest analogues each cover only one piece: Viability (imagery, developer sites), PropMarker (floorplans, conversions) and PropertyData (large-plot and title-split screens).

### Gaps
- Could not search for other 2023–26 imagery startups, for example "extension potential AI", "backland AI", "Resi", "PropertyHeads" or Getmapping/Bluesky-based consumer tools. The search budget ran out, so this list may be incomplete.

## Q7. Gap analysis: what none of them do well for spotting value-add potential in on-market houses

### Takeaway
Incumbents screen on-market houses for *price* opportunity (BMV, reductions, yield) and land parcels for *planning* opportunity. **None found joins the two**: an automated, per-listing assessment of the physical and planning upside of an ordinary house (extend, convert, sever the garden, replace), backed by street-level precedent and sold-price uplift, at an investor-friendly monthly price.

### Cited Findings (evidence underpinning the gaps)
- Investor tools' "deal" logic is price- and motivation-based:
  - BMV vs comps, reductions and fall-throughs (Property Filter) — [PropDetect review](https://propdetect.com/compare/property-filter-review)
  - Cashflow, equity and exit-speed scores (PropDealAI) — [PropDealAI](https://propdealai.com/)
  - Yield and ROI overlays (PaTMa) — [PaTMa](https://www.patma.co.uk/property-prospector/)
  - Refurb and exit modelling (PropDetect) — [PropDetect](https://propdetect.com/)
- PropertyData's development-flavoured screens are categorical strategies ("Large plot", "Unbroken freeholds", "Near large development") rather than a modelled development-potential score — [PropertyData](https://propertydata.co.uk/source-on-market)
- Land tools centre on titles and land parcels, direct-to-owner letters and planning constraints, sold on annual contracts. For example, Searchland Standard includes "direct-to-owner letter sending" with a 12-month minimum — [Searchland pricing](https://searchland.co.uk/pricing). Searchland's PD tooling targets Class MA commercial-to-residential — [Searchland PD](https://searchland.co.uk/blog/searchland-unveils-new-permitted-development-search-tool).
- The only floorplan-based potential detection found is internal layout (extra bedroom, HMO, conversion), not external extension or plot potential — [PropMarker](https://propmarker.co.uk/)
- The only imagery-based UK startup found targets developer site viability, not listings — [Bluesky/Viability](https://bluesky-world.com/2024/12/05/high-resolution-aerial-imagery-from-bluesky-applied-in-revolutionary-new-ai-tool-launched-to-support-uk-housing-developers/)
- £/m² data exists (Housemetric), but no tool was found estimating **post-works GDV from extended or improved neighbours' sold prices** — [Housemetric](https://housemetric.co.uk/)

### Inferences (candidate white space for the startup; these are inferences, not verified absences)
1. **Extension potential per listing.** Compute PD allowances and likely planning outcomes (rear, side-return, loft, double-storey) against the house footprint and garden depth from aerial imagery or OS footprints. No incumbent was found doing this.
2. **Garden-plot, backland and severance potential.** Combine plot width and depth, road frontage and access, and plot size *relative to neighbours on the street* with INSPIRE polygons. PropertyData's "Large plot" is the nearest, and it appears to be a crude size threshold.
3. **Street-level planning precedent.** "3 of 5 neighbours have approved two-storey rear extensions; median approval 2019–2025." PaTMa and SiteLens alert on applications but do not link precedent to a specific listing's upside.
4. **Uplift valuation.** GDV based on comparables that have *already done the works* (extended or improved sold comps, £/m² uplift), netted against build costs to give a flip margin. PropDetect models refurb exits but not planning-gain exits.
5. **Replacement-dwelling or redevelopment flags** for bungalows or low-density houses on large plots. No tool was found targeting this.
6. **Price point and terms.** A self-serve £30–£150/month product with development-potential scoring would sit between investor tools (£4–£250, price-focused) and land tools (£195+/licence annual, land-focused).
7. **Keyword and NLP on listing text** (for example "STPP", "potential to extend", "large garden", "development potential", "no chain", "requires modernisation") combined with the geospatial checks above. The evidence did not show any incumbent pairing listing-text NLP with plot or planning analysis. PropertyEngine and Property Filter have strong alerts, but their keyword capabilities could not be confirmed.
- **Competitive risk:** PropertyData (data breadth, cheap, already has large-plot and title-split screens), Searchland and LandHunt (AI plus planning, moving down-market) and PropMarker (AI plus floorplans) are the most plausible fast followers.

### Gaps
- Findings on "absence" are limited by the blocked page fetches and exhausted search budget. The gap claims above should be validated by hands-on trials of PropertyData (Plot Map and Large plot), PropMarker, LandHunt and the Searchland AI assistant before being used in investor materials.
- The Rightmove/Zoopla data products (for example Rightmove Data Services, Zoopla/Hometrack) were not researched. Portals could add development-potential tags themselves, which is an unassessed risk.
