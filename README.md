# W4H Sample ICDE Demo CSV Importer

Notebook + CLI to import the paired sample package **[w4h-sample-icde-demo-csv](https://github.com/USC-InfoLab/w4h-sample-icde-demo-csv)** into W4H. Credentials stay in a local `.env` (never committed).

**Publisher:** usc-infolab · **Kinds:** notebook, CLI · **Language:** Python

Unlike the Fitbit importer, this package includes a `gps_track` signal (`geo: {lat, lon}` in its GeoMTS mapping) — use it to exercise the geo branch of import/mapping tooling end to end, not just the non-geo one.

## Who should do what

| Role | What to do |
|------|------------|
| **Admin** | Adapt the notebook for your export shape, then ingest into **your team's** catalog. Use the CLI (`import` / `sync`) for cron and incremental updates. |
| **User** | Use analysis contributions against loaded datasets. You cannot add datasets or edit raw tables. |
| **Super admin** | May seed/replace canonical **W4H Samples** datasets. Everyone else treats sandbox as read. |

## Prerequisites

- Running **w4h-api** and a personal API key (Profile → API keys)
- Clone this repo **next to** the sample package:

```
W4H/
  w4h-sample-icde-demo-csv/
  w4h-sample-icde-demo-csv-importer/
```

## Credentials

```bash
cp .env.example .env
# Edit .env — set W4H_API_KEY (and W4H_DATASET_ID)
```

Never commit `.env` or paste keys into notebook outputs.

## Install

```bash
pip install -e ".[dev]"
```

## One-command run (`run.sh`)

```bash
./run.sh import          # or: ./run.sh sync --signal heart_rate --file ...
```

Bootstraps a local `.venv`, installs this package, and runs the CLI. If `W4H_API_KEY` isn't already set in your environment, it prompts for it (and the API base URL) interactively and offers to save both to `.env`. Set `W4H_API_KEY`/`W4H_API_BASE` in the environment beforehand to run it non-interactively — this is the same entrypoint the in-app "Run" trigger uses.

## Notebook (primary)

Open [`notebook/import_icde_demo_csv.ipynb`](notebook/import_icde_demo_csv.ipynb). It loads `manifest.yaml` from the sample repo, shows GeoMTS mapping (including `gps_track`'s geo role), and posts chunked rows to `POST /datasets/:id/import/csv-batch`.

Admins: run the import cells against a dataset you created.
Users: run through mapping/preview; skip `mode="replace"` on W4H Samples.

## CLI import (admins)

```bash
export W4H_API_KEY=w4h_sk_...   # or use .env
w4h-sample-icde-demo-csv-import import --dataset-id sample-icde-demo-csv --mode replace
```

## Incremental sync (cron)

```bash
w4h-sample-icde-demo-csv-import sync --dataset-id sample-icde-demo-csv --signal heart_rate --file /path/to/new_heart_rate.csv
```

Use `sync` without `--file` to re-read the sample package CSV (dedupe skips existing rows).

## Tests

```bash
pytest tests/test_manifest.py -q
```

Optional API tests:

```bash
export W4H_API_KEY=...
export W4H_DATASET_ID=sample-icde-demo-csv
pytest tests/test_import_api.py -m integration -q
```

## API

Uses `POST /datasets/:id/import/csv-batch` (no direct database access). Sends an explicit `table_prefix: "icde_demo"` in every payload so physical tables don't collide with other vendors (e.g. `fitbit`) sharing a signal slug like `heart_rate` in the same dataset schema — see [ADR-016](https://github.com/USC-InfoLab/w4h-docs/blob/main/dev/ADR-016-paired-sample-importer-repos.md).
