# RE-Project

Screen every house for sale in Cambridge for **development potential**: new dwellings in gardens or
side plots, larger replacements, subdivision. The screen uses the listing, satellite imagery, the
neighbours, planning history and sold prices.

**Current stage: v0.** Before building anything, we run the entire workflow by hand. That gives us
a labelled gold set, and it lets us test whether a multimodal model makes the same calls we do.

| File | What |
|---|---|
| [`docs/spec-v0.md`](docs/spec-v0.md) | What v0 is, pipeline, **pass/fail criteria**, phases |
| [`docs/rubric.md`](docs/rubric.md) | How to judge a property. Shared by humans and the model |
| [`docs/manual-run.md`](docs/manual-run.md) | Step-by-step runbook for the manual run |
| [`templates/packet.md`](templates/packet.md) | Per-property evidence packet (copy one per property) |
| [`prompts/site-assessment-v0.md`](prompts/site-assessment-v0.md) | Model prompt for the zero-code model run |
| [`eval/*.csv`](eval/) | Headers for the labels, properties and friction-log sheets |

Start with `docs/manual-run.md` → Phase 0 (pilot on 5 properties).
