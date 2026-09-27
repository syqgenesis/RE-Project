# CB1 flip-feasibility analyser

Give it a listing link or an address. It tells you whether the house works as a flip (refurb,
extension/loft, or split/plot sale), the **maximum purchase price** by the residual method, and
what's still unresolved. Method: [`PLAN.md`](PLAN.md).

It runs **on your Mac**, next to your Postgres database and your Claude Code login. The LLM steps
use your Claude subscription through `claude -p` (model `claude-opus-5-5`), not an API key.

## Setup (once)

```bash
cd RE-Project
git pull origin claude/confident-shannon-2g1hmm
python3 -m venv .venv && .venv/bin/pip install -e ".[dev]"
cp .env.example .env            # set DATABASE_URL (a read-only role is best)
claude                          # make sure you're logged in, then /exit
.venv/bin/python -m flip check  # shows what's connected
```

Optional data that makes results much better:

| Put here | What | Where from |
|---|---|---|
| `data/ppd/*.csv` | HMLR Price Paid, last 3 years | GOV.UK "Price Paid Data" yearly files |
| `data/inspire/*.gml` | Freehold plot polygons (Cambridge) | use-land-property-data.service.gov.uk → INSPIRE |
| `EPC_API_TOKEN` in `.env` | Floor areas for comps and the subject | EPC register API |

Without Price Paid files there are no comps, so every case comes back `INSUFFICIENT_EVIDENCE`.

## Run

```bash
.venv/bin/python -m flip discover          # maps your DB schema -> config/db_mapping.yaml; check it
cp cases/cases.example.yaml cases/cases.yaml   # add your cases
.venv/bin/python -m flip run cases/cases.yaml
```

Each case writes `runs/<case_id>/report.md` (verdict, strategies, sensitivity, comps, planning
with neighbour precedent, imagery, constraints, evidence ledger) and `result.json`.
`runs/summary.json` lists all verdicts.

Flags: `--no-llm` (rules and code only), `--no-web`, `--no-db`, `--case case1`.

## What each step uses

| Stage | Code | LLM (Opus 5.5 via Claude Code) |
|---|---|---|
| A Identify | listing parse, postcodes.io, EPC match | — |
| B Eligibility | CB1, tenure, INSPIRE plot, planning.data.gov.uk constraints | — |
| C Condition | photo download, scope mapping | grades photos 1–4 |
| D Planning | your DB (subject + neighbours), readability, regex triage, precedent table | triages unmatched descriptions; reads documents of material ones |
| E Imagery | Esri current + Wayback history, your manual captures | compares dated images |
| F Comps | Price Paid + EPC £/m², quantiles, street ceiling | sense-checks comps; code recomputes |
| G Schemes | PD rules, geometry thresholds, values | — |
| H–I Appraisal, verdict | residual max price, sensitivity, rules | — |
| J Report | tables, ledger, number check | narrative (may not add numbers) |

All assumptions (costs, SDLT, finance, hurdles) are in `config/assumptions.yaml`.

## Tests

`.venv/bin/python -m pytest` covers finance/SDLT, planning triage rules, the DB adapter (against a
throwaway Postgres if installed), parsers and end-to-end golden cases.
