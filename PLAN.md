# Plan: CB1 flip-feasibility analyser (analysis design, v1)

## Context

The project pivots from the v0 "development-potential screener" to a **flip-investor tool**. An
investor supplies a listing link or an address. The system returns whether the house is a credible
flip, under which strategy, the **maximum purchase price**, and the conditions still unresolved.

The user asked for:
- a plan grounded in professional investor practice;
- existing ChatGPT draft expanded to say exactly **how** each step is analysed: code vs LLM,
  which model, and what architecture;
- freehold only, listed buildings excluded;
- planning analysis that reads each application's one-line description (the "blob") first and only
  opens the documents if it matters to a flip;
- satellite plus historical aerial imagery.

The user's local database isn't available yet ("will give later"). The user also asked for **all
current repo files to be deleted**, to start from scratch.

## 0. Repo reset (first action after approval)

- Delete every tracked file: `README.md`, `docs/`, `templates/`, `prompts/`, `eval/`.
- Commit "Start from scratch" on `claude/confident-shannon-2g1hmm` and push.
- The v0 content stays in git history, and `origin/claude/loving-davinci-qo8x5u` is left untouched.

## 1. What the system decides

**Inputs**
- Required: a listing URL or an address.
- Optional: investor profile (company or individual, cash or bridging, target margin).

**Output: the Flip Report**
- **Verdict**, one of:
  - `VIABLE`: base case and downside both pass.
  - `CONDITIONAL`: works below price X, or once condition Y is resolved.
  - `NOT_VIABLE`
  - `EXCLUDED`: leasehold, listed, or outside CB1.
  - `INSUFFICIENT_EVIDENCE`
- **Per strategy**: gross development value (GDV), total cost, profit, profit on cost, peak cash,
  duration and maximum purchase price.
- **Evidence ledger**: every fact tagged `verified | estimate | inference | unknown`, with source
  and date.

**Three strategies, each appraised independently.** No strategy inherits another's value.

| Strategy | What it is | Value lever |
|---|---|---|
| **Refurb flip** | Buy tired, renovate within the existing footprint, sell | Condition uplift |
| **Extension / loft flip** | Add floor area (permitted development (PD) or full planning), refurb, sell | £/m² × added m² |
| **Split / plot sale** | Get planning permission to separate part of the land (e.g. a garden plot or side plot for a new house) or to convert into 2+ flats, then sell the plot or units separately from the house. Profit = plot or unit value − the value lost by the main house | Planning gain |

## 2. Professional basis

This is what UK flip underwriters and development appraisers do:

1. **Screen hard exclusions cheaply first**: tenure, listing, location.
2. **Resale value (ARV/GDV) from sold comparables**, never from asking prices, and with no
   market-growth assumption.
3. **Full cost stack**: purchase, SDLT (additional-dwelling / company rates, from config), legal,
   survey, works + 10–20% contingency, fees, planning, bridging interest (≈0.55–1.1%/month,
   65–75% LTV), holding costs (council tax, insurance, utilities), selling costs.
4. **Hurdle checks** (profit, profit on cost, duration) plus a **stress test**.
5. **Maximum offer** solved backwards from the hurdle.
6. **Desktop to physical**: whatever desktop research can't establish becomes a pre-exchange
   check (RICS Level 3 survey, title and covenants, contractor quotes).

This follows RICS development-appraisal practice (residual method plus sensitivity). The ChatGPT
draft's thresholds become **config defaults, not hard-coded**: ≥ £50k profit, ≥ 20% profit on cost,
≤ 12 months, 15% contingency, and downside of resale −10% / works +15% / +3 months must be
non-loss-making.

## 3. Architecture

**Pattern: a deterministic, code-orchestrated pipeline, not a free-roaming agent.** Every stage is
a Python function with typed inputs and outputs (Pydantic). LLM calls appear only at named nodes
that need reading or vision, and every LLM output is schema-constrained (structured outputs).

Why a pipeline:
- it's auditable, cheap to re-run and testable per stage;
- it early-exits on exclusions before any expensive calls;
- arithmetic never touches the LLM.

```
input → A Identify → B Eligibility gate ──(EXCLUDED)──► report
                         │
         ┌───────────────┼──────────────────┬───────────────┐
         C Condition     D Planning          E Imagery       F Comps / GDV
         (vision LLM)    (rules + LLM)       (code + vision) (code)
         └───────────────┴────────┬─────────┴───────────────┘
                   G Scheme builder (rules engine + LLM for feasibility notes)
                   H Residual appraisal + sensitivity (code only)
                   I Verdict rules (code) → J Report writer (LLM, facts-only) → Flip Report
```

**Stack**
- Python 3.12.
- Pydantic v2: a Python library that defines the exact shape of each stage's data (field names,
  types, allowed values) and rejects anything malformed. It's the contract between stages, and it
  gives the schema the LLM's structured output must match.
- Storage: DuckDB for the local cache and evidence ledger. It reads the user's DB via an adapter
  once its format is known.
- `httpx` for public APIs; Playwright only where no API exists.
- `shapely` / `pyproj` for geometry. `pymupdf` for PDF text, with Claude reading the PDF pages
  directly as the primary reader (it handles scans natively).

**LLM runtime: your Claude subscription, via Claude Code. No API key, no per-token billing.**

- The Python pipeline calls Claude Code in headless mode for each LLM node:
  `claude -p <prompt> --model claude-opus-5-5 --output-format json`.
  - The prompt file comes from `llm/prompts/`.
  - The inputs (text, image paths, PDF paths) are passed as files Claude Code reads.
  - The returned JSON is validated against the node's Pydantic model. If it's invalid, the call is
    retried once with the validation error included.
- Authentication is your existing Claude login (`claude` → `/login`) on the machine running the
  pipeline. Usage counts against the subscription's limits, not a bill.
- **Model: Claude Opus 5.5 (`claude-opus-5-5`)**, the newest, at every LLM node.

| Node | Mode | Why |
|---|---|---|
| Planning deep-dive, scheme feasibility, comps sense-check, report writer | One call per task, thorough prompt | Judgement-heavy, low volume |
| Vision: condition grading, imagery change detection | One call with all images as files | Multi-image comparison |
| Planning-description triage (subject + neighbours) | **Chunked**: ~50 descriptions per call, returning a JSON list | High volume. Chunking keeps the call count low under the usage limits |

What changes vs. the pay-per-token API:
- No Batch API, prompt-caching controls or native citation blocks.
- Instead, **page citations are enforced by the output schema**: every extracted planning fact must
  carry `{doc_id, page}`, and code checks the page exists.
- Throughput is bounded by the subscription's usage limits. The runner is resumable: it caches
  each node's output by input hash, so an interrupted run continues without redoing calls.
- If this later becomes a product used by other investors, those LLM calls would move to API keys.
  Subscription use is for your own analysis.

## 4. Stage-by-stage method

### A. Identify the property (code, with an LLM fallback)
- **Code**: parse the listing (Rightmove/Zoopla page JSON, or an address the user pastes).
- **Code**: resolve the exact address and **UPRN**.
  - Match candidates from the EPC register for that postcode on floor area, EPC score and property
    type.
  - Confirm with OS Places / AddressBase if a key is available; otherwise use the EPC UPRN.
- **LLM (vision, only if the above is ambiguous)**: compare listing photos with Street View
  frames of the candidate houses.
- **Output**: UPRN, lat/lon, CB1 check (reject outside CB1), and an identity confidence. On
  conflict → `INSUFFICIENT_EVIDENCE`.

### B. Eligibility gate (code; stops early)
- **Tenure**:
  - HMLR INSPIRE polygon ⇒ a freehold title exists for the land.
  - The listing tenure field is text-parsed.
  - **HMLR title register (£7, manual/API)** is the verified proof. Until it's pulled, tenure is
    `estimate`.
  - "Share of freehold" = excluded.
- **Listing**:
  - Point-in-polygon of the plot against Historic England NHLE listed-building points and polygons.
  - Also flag listed buildings **adjacent** to the plot, as a curtilage-listing risk that needs
    manual confirmation.
  - A name search alone never counts as clearance.
- **Also recorded (not exclusions)**: conservation area, Article 4 directions, tree preservation
  orders (TPOs), flood zone, Green Belt. Sources: planning.data.gov.uk API, EA Flood Map for
  Planning, Greater Cambridge layers.

### C. Existing condition (vision LLM → structured grades)
- Input: listing photos, floorplan and EPC data (heating, walls, glazing, recommendations).
- LLM output, per area (kitchen, bathroom, electrics signals, windows, roof, damp signs, layout):
  a grade on a 1–4 scale, observed evidence and the photo index.
- Code maps the grades to a refurb scope, e.g. *light / medium / heavy / structural*, and
  £/m² cost bands from a **user-editable cost table**.

### D. Planning: blob-first triage (the core of your requirement)
- **D1. Readability check (code).** For each application:
  - Normalise the description, ref, dates and decision.
  - Validate it: non-empty, not truncated, decodable text, ref matches the pattern `\d{2}/\d{5}/[A-Z]+`.
  - Status: `readable | partial | unreadable | missing`.
  - **Unreadable never silently becomes irrelevant**: it goes to `uncertain`.
- **Scope: subject property and neighbours, both screened.** Code pulls every application:
  - on the subject UPRN;
  - on the adjoining and opposite properties;
  - on the same street;
  - within ~150 m for similar house types.
  Neighbour decisions carry nearly as much weight as the subject's own history. They show what the
  planners actually approve or refuse here: extension depths, dormers, garden dwellings, and the
  refusal reasons.
- **D2. Relevance triage (rules first, then LLM).**
  - Rules layer: a regex taxonomy. That's a fixed list of keyword patterns, each mapped to a
    category (e.g. "replacement window*" → routine, "erection of * dwelling" → material). It
    labels the obvious cases instantly, for free and the same way every time, so the LLM only sees
    the ambiguous descriptions.
    - Obvious **routine**: replacement windows/doors, satellite dish, fence, tree works on
      non-subject trees, signage, boiler flue.
    - Obvious **material**: extension, loft/dormer, erection of dwelling, subdivision/conversion,
      change of use, demolition, "land rear of/adjacent", enforcement, removal/variation of
      condition, certificate of lawful development (CLUED/CLOPUD), prior approval (larger home
      extension), listed building consent.
  - Anything unmatched goes to the LLM (in chunks), which returns
    `{relevance: material|routine|uncertain, flip_link: refurb|extension|split|value|none, reason}`.
  - Window exception: a "routine" item on the **subject** property is escalated if its type
    (listed building consent, conservation area) or conditions imply restrictions. Rule example:
    any listed building consent on the subject → material.
- **D3. Deep dive (material and uncertain only).**
  - Code fetches the document list: decision notice, officer/delegated report, approved drawings.
  - Opus 5.5 reads the PDFs and extracts the following, each with `{doc_id, page}`:
    - decision and date;
    - **conditions**, especially any **removing PD rights** (critical for the extension flip);
    - refusal reasons;
    - approved dimensions;
    - whether it's implemented, lapsed or superseded.
  - **Neighbour precedent extraction** (same deep-dive on material neighbour applications):
    - scheme type, approved depth/height, decision;
    - the officer's key reasoning (e.g. "45° rule met", "harm to street scene", "overlooking");
    - distance and similarity to the subject.
  - Code aggregates these into a **precedent table**: per scheme type, approvals vs refusals nearby,
    the typical approved size, and the recurring refusal reasons. It feeds the consent likelihood
    in G. It's labelled as context, not permission for the subject.
- **Output**: the subject's planning chronology, its PD-rights status, and the neighbour precedent
  table.

### E. Imagery: current and historical (code fetches; vision LLM compares)
- **Current**: satellite tile at fixed scale centred on the UPRN (Google Maps Static API or Esri
  World Imagery), with the INSPIRE polygon overlaid in code. Plus Street View front and side.
- **Historical**:
  - Google Earth Pro historical imagery (no API; manual capture step in v1, logged).
  - Esri Wayback releases (API, several dates).
  - **Cambridge University Collection of Aerial Photography** and Historic England aerial archive
    for older dates (manual).
- **Geometry (code, not the LLM)**: plot area, rear-garden depth, frontage and side gaps, from the
  INSPIRE polygon and OS building outlines.
- **Vision LLM**, given before/after pairs plus the date metadata:
  - footprint or roof change (extension, dormer, outbuilding);
  - garden loss; new neighbouring backland houses;
  - side/rear access.
  - Each observation carries image, date and confidence.
- **Code reconciliation**: each visible change is matched against the D chronology. A change with
  no matching consent is flagged `possible unauthorised works → verify` (it affects the lawful
  baseline and PD allowances).

### F. Resale value / GDV (code; LLM only for comp rationale text)
- Comps from HMLR Price Paid joined to the EPC register (floor area). Filter:
  - same type;
  - ≤ 0.5 mi and ≤ 12 months, expanding transparently when there are fewer than 3;
  - a condition proxy (e.g. recent sale after an extension, from E/D, counts as "done-up").
- Output:
  - adjusted £/m² (median, IQR);
  - separate **"as-is" vs "refurbished" value bands**;
  - for extension flips, the value of the added m² at a *discounted* marginal £/m² (a ceiling
    check against the street's top sale).
- Rule: no asking prices in GDV; they're supporting evidence only.
- **LLM sense-check (Opus 5.5, high effort), then code recompute.**
  - The LLM reviews the code's comp set and value bands against the listing, photos, floorplan and
    comp details. It looks for bad comps: different condition, a flat mis-typed as a house, an
    outlier sale, the wrong street context. It also checks for implausible values, e.g. a GDV above
    the street ceiling.
  - It returns structured **adjustments**: `exclude comp X | add weight to Y | flag band`, each
    with a reason.
  - **Code applies the adjustments and recomputes.** The LLM never types the final number itself,
    so the arithmetic stays exact and auditable.
  - The report shows both the pre- and post-review values and every change made.
  - Guardrail: if the reviewer moves GDV by more than ±10%, the verdict is capped at `CONDITIONAL`
    pending human review.

### G. Scheme builder (rules engine + LLM)
- **Refurb**: scope from C.
- **Extension**: a **PD eligibility engine in code** covering Class A (rear/side, including the
  larger-home-extension prior approval) and Class B (loft volume 40/50 m³). It checks house type,
  previous extensions (E), Article 4 and PD-removal conditions (D), conservation area and flood
  zone. If PD isn't available → full-planning route, with a precedent-based likelihood from D.
- **Split / plot**: geometry tests from E (depth, access width, frontage) plus precedent from D.
  The route is always full planning.
- **LLM (Opus)** writes feasibility notes per scheme from the structured facts only, and lists what
  would need a site visit (party wall, drainage, trees).

### H. Financial model: basic residual method (code only, unit-tested)
Per strategy:

**Maximum purchase price (residual)** = GDV − works (incl. contingency) − fees (planning,
professional, legal, survey) − finance − holding − selling costs − SDLT − target profit
(e.g. 20% of cost)

- SDLT depends on the price, so the calculation iterates a few times until the price stabilises.
- Finance is a simple term: rate × borrowed amount × months, plus fees.
- Assumptions (rates, contingency, target profit, SDLT bands) live in a dated config file.

**Also reported at the asking price**: profit and profit on cost.

**Simple sensitivity table**: profit and maximum price when
- GDV is −10% / −5% / base / +5%;
- works cost is base / +15%.

Verdict uses the base case plus the "GDV −10%, works +15%" corner.

### I. Verdict (code)
Deterministic rules over the H outputs and evidence status:
- `VIABLE`: asking price ≤ maximum price in the base case, and profit ≥ 0 in the stress corner.
- `CONDITIONAL`: the deal only works below the asking price, or tenure is still an `estimate`.

### J. Report (Opus, facts-only)
- The LLM gets the structured results plus the evidence ledger, and writes the narrative.
- It may not introduce numbers: a code post-check diffs every number in the text against the
  ledger.
- Rendered as Markdown/HTML with the annotated imagery.

## 4b. Your database (to be filled in by you before implementation)

**What we know so far** (from the paths you shared; they're on your Mac, so this cloud session
can't open them):

| Location (on your Mac) | What it is | How the pipeline uses it |
|---|---|---|
| `…/RE-Project/.local/pgdata` | A **local PostgreSQL** data directory, being appended to live | Primary store. Read over a normal Postgres connection, never by touching these files |
| `…/RE-Project/.local/` (other folders) | Downloaded source files (planning PDFs etc.) and collection logs | The document store for stage D3. Paths are referenced from DB rows |
| `~/Documents/ChatGPT/RE Project/collection` | Collection status and exports | Coverage and freshness report; not an analysis input |

**Design consequences**
- **Run location**: the pipeline runs **on your Mac**, next to Postgres, the source files and your
  Claude Code login. This cloud session writes the code; you run it locally.
- **Read-only access**: a dedicated `flip_reader` Postgres role with `SELECT` only. Connect via
  `psycopg` using `DATABASE_URL` from a local `.env` (never committed).
- **Live appends are safe**: each analysis reads inside one `REPEATABLE READ` transaction, so it
  sees a consistent snapshot while collection continues. It records the snapshot time in the
  evidence ledger.
- **Never copy `pgdata` while Postgres is running**: the copy would be corrupt. To share the
  structure, run `pg_dump --schema-only` plus a small sample export. That's the input I need to
  write `sources/user_db.py`.
- **Freshness**: each property's report states when its planning data was last collected (from
  the collection logs/status). Stale rows trigger a live refresh from the planning portal.

**Still to fill in (by you, before implementation)**
- Output of `pg_dump --schema-only` (tables, columns, keys).
- Which column holds the one-line proposal description.
- How documents link to applications (file path column? URL?).
- How applications link to an address or UPRN.

## 4c. Execution handoff: run on your Mac

This cloud session can't reach your Mac, so the analysis runs in a Claude Code session **on your
Mac**. Start it in the project folder with either:
- the Claude Desktop app, pointed at `…/RE-Project`; or
- `claude remote-control` in a terminal there. The session then shows up in the Claude Code app.

In that session, pull `PLAN.md` from `claude/confident-shannon-2g1hmm`. It then does M0 from the
files that already exist (**the DB structure is in them; nothing more is needed from you**):
1. Read the schema directly:
   - the collection code/migrations in `.local/` and the project folder;
   - `information_schema` via a read-only connection to the running Postgres;
   - the exports in `…/RE Project/collection`.
2. Write the discovery report:
   - tables and row counts;
   - which column is the one-line description;
   - document links, and address/UPRN keys;
   - the readability status of descriptions and document files.
3. Build `sources/user_db.py`, then continue M1→M5 per this plan.

## 5. Data sources

| Need | Source | Access |
|---|---|---|
| Listing | Rightmove / Zoopla / OnTheMarket | Scrape/parse (note ToS); or manual paste |
| Address / UPRN | EPC register API, OS Places | Free key (EPC); OS key |
| Plot boundary | HMLR INSPIRE polygons | Bulk GML, OGL |
| Tenure proof | HMLR title register | £7 per title |
| Listed / conservation / Article 4 / TPO / Green Belt | Historic England NHLE; planning.data.gov.uk API | Free, OGL |
| Flood | EA Flood Map for Planning | Free |
| Planning | **Your local DB** first; Greater Cambridge public access (Idox) for refresh and documents | Adapter + fetch |
| Comps | HMLR Price Paid + EPC | Bulk CSV / API |
| Imagery | Google Static Maps / Street View, Esri Wayback, Google Earth Pro (manual), CUCAP / Historic England (manual) | Keys; manual steps logged |

Your DB is the first source for planning (and anything else it holds). Newer authoritative data
overrides it, and the discrepancy is recorded.

## 6. Repo layout (after reset)

```
flip/
  pipeline.py            # orchestrates A→J, early exit, ledger
  models.py              # Pydantic schemas (Property, Evidence, Scheme, Appraisal, Report)
  stages/identify.py  eligibility.py  condition.py  planning.py  imagery.py
         comps.py  schemes.py  finance.py  verdict.py  report.py
  sources/               # one adapter per data source (+ user_db.py once DB is known)
  llm/runner.py          # headless `claude -p` wrapper: schema validation, retry, result cache
  llm/prompts/           # triage.md, condition.md, imagery.md, deepdive.md, report.md
config/assumptions.yaml  # hurdles, cost table, SDLT bands (dated), finance terms
tests/                   # finance unit tests + golden cases
evals/                   # labelled triage set, golden properties, scoring script
```

## 7. Milestones

1. **M0.** Repo reset. Receive the DB and write a read-only discovery script: schema, row counts,
   blob readability report.
2. **M1.** A + B (identify, eligibility) with the evidence ledger.
3. **M2.** D planning triage + deep dive, evaluated on a labelled set of ~200 CB1 descriptions
   drawn from your DB.
4. **M3.** E imagery (current + Esri Wayback, geometry), plus the manual historical capture step.
5. **M4.** F + G + H + I: comps, schemes, residual appraisal, verdict.
6. **M5.** J report, the golden-case evals, and a run-time / subscription-usage report.

## 8. Verification

- **Finance**:
  - unit tests with hand-calculated residual cases;
  - an independent spreadsheet recalculation for 3 deals;
  - at the maximum price, profit equals the target ± £100.
- **Comps sense-check**:
  - seeded bad comps (a flat, an outlier, an unrefurbished sale) must be excluded;
  - on clean comp sets the reviewer must make no change.
- **Triage eval**: ~200 human-labelled descriptions. Targets:
  - **recall on material ≥ 98%** (missing a PD-removal condition is costly);
  - routine precision ≥ 90%;
  - 0 unreadable blobs classed as routine.
- **Golden properties** (end to end):
  - freehold pass; leasehold and share-of-freehold excluded; tenure unresolved;
  - listed; possible curtilage listing; conservation-area-eligible house;
  - window application screened out; "minor" application escalated because of listed building
    consent or PD removal;
  - scanned, missing and unreadable documents;
  - aerial change with no consent;
  - weak comps; extension adding too little value; deal failing the downside test.
- **Report integrity**: automated check that every number in the narrative exists in the ledger.

## 9. Open items needed from you
- The local DB: file, or schema + sample.
- Claude Code installed and logged in with your subscription on the machine that runs the pipeline
  (where your DB lives).
- Data keys: Google Maps Platform, EPC register, optionally OS.
- Default investor profile, for SDLT and finance.
- Environment network allowlist for the data sites above (currently blocked in this cloud
  sandbox).
