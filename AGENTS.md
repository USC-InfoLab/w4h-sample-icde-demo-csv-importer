# AGENTS.md — w4h-sample-icde-demo-csv-importer

Importer for the paired **`w4h-sample-icde-demo-csv`** package (geo + non-geo signals): notebook + CLI + `run.sh` + tests. Human workflow: [README.md](./README.md). The shared W4H architecture overview is at the end of this file.

## Where this repo fits in W4H

- **Layer:** contribution, kinds `notebook` + `cli`, catalog slug `w4h-sample-icde-demo-csv-importer`, **`runnable = true`**.
- **Role:** the second sample importer. It exists to push the **geo** signal (`gps_track`) and a **5-minute** interval through the same `csv-batch` ingest path as Fitbit. In the app's **Run import...** dialog it is the "ICDE demo CSV" choice next to Fitbit.
- **Structure mirrors `w4h-sample-fitbit-csv-importer`** (`client.py`, `config.py`, `manifest.py`, `vendor_spec.py`, `csv_import.py`, `__main__.py`, `run.sh`). When fixing a bug in one, check the other.
- **Downstream:** creates `ds_<dataset_id>.icde_demo_*` tables + `w4h.tables` mappings, including `sampling_interval: 5min`, which `w4h-sql-compute-mets` reads to scale its formula.

## Data path

```text
../w4h-sample-icde-demo-csv/manifest.yaml + data/*.csv
  → csv_import.py: 500-row chunks → POST /datasets/:id/import/csv-batch
       table_prefix = TABLE_PREFIX = "icde_demo"
  → stdout "@@PROGRESS@@ {json}" lines for the runner
```

## Commands

| Command | Purpose |
|---|---|
| `pip install -e ".[dev]"` | Install + pytest |
| `./run.sh import [--mode append\|replace]` | Same entry point as in-app Run |
| `pytest tests/test_manifest.py tests/test_vendor_spec.py -q` | Offline tests |
| `pytest tests/test_import_api.py -m integration -q` | Needs a running `w4h-api` + key + dataset id |

Env: `W4H_API_KEY`, `W4H_API_BASE`, `W4H_DATASET_ID`, `W4H_SAMPLE_ICDE_DEMO_CSV_PATH` (default `../w4h-sample-icde-demo-csv`).

## Contracts

- **`table_prefix: "icde_demo"` in every payload.** Without it, `heart_rate` here would collide with Fitbit's `heart_rate` in the same `ds_*` schema.
- `run.sh` + `@@PROGRESS@@` follow the same contract as the Fitbit importer (`w4h-api/lib/contribution-runner.js`).
- Only `POST /datasets/:id/import/csv-batch` and `GET /datasets`.

## Hard boundaries

- API key only in local `.env` or the environment.
- No direct Postgres or free SQL (ADR-023). Analytics belong in `w4h-sql-compute-mets`-style packages.

## Git expectations for agents

- Do not `git commit` or `git push` unless the user asks.
- Manifest or geo changes need a paired PR in `w4h-sample-icde-demo-csv`.

<!-- BEGIN w4h-system-overview: identical in every W4H repo's AGENTS.md. Edit all copies together. -->

## W4H system overview (shared across all repos)

**W4H (Wearables for Health) Toolkit** loads wearable-device data into PostgreSQL, organizes it by team, project and dataset, controls access, and runs curated analyses on it. Each signal is a **GeoMTS** (Geospatial Multivariate Time Series) table whose roles (`subject`, `time`, optional `geo`, `values[]`) are stored in `w4h.tables.mapping_json`, not in fixed column names. Three repos form the platform, one packages it, and the rest are **contributions** listed in the in-app catalog (`w4h.contributions`).

| Repo | Role |
|---|---|
| `w4h-api` | Express API and Postgres DDL (`w4h` schema): auth, ACL, ingest, catalog, contribution runner, SQL engine. Port 2026 |
| `w4h-app` | Vue 3 + Vite SPA; talks only to `w4h-api`. Port 5173 |
| `w4h-docs` | Product rules, MVP, ADRs and guides; imported by the API as in-app Help. Owns product decisions |
| `w4h-docker` | Compose stack (`api`, `app`, `notebooks`) built from sibling repos; Postgres is external |
| `w4h-sample-fitbit-csv`, `w4h-sample-icde-demo-csv` | Synthetic sample CSVs plus `manifest.yaml` (ICDE includes a `gps_track` geo signal) |
| `w4h-sample-fitbit-csv-importer`, `w4h-sample-icde-demo-csv-importer` | Runnable importers (notebook, CLI, `run.sh`) for those samples |
| `w4h-fitbit-csv-file-importer` | Runnable importer for user-supplied Fitbit CSVs: profile headers, review a drafted mapping, ingest |
| `w4h-sql-compute-mets` | SQL contribution (YAML + SQL template) that `w4h-api` executes in-process |
| `fft_approximate` | Postgres C extension, catalog slug `fft-approximate`; no API involvement |
| `w4h-demo-approximate-queries` | Notebook comparing `fft_approximate` with exact averages over direct Postgres |

**Main flows:**

1. **Ingest:** importers post 500-row chunks to `POST /datasets/:id/import/csv-batch`. `lib/ingest-csv.js` creates `ds_<dataset_id>.<table_prefix>_<signal>` and upserts its `w4h.tables` mapping.
2. **In-app Run (ADR-022):** `POST /contributions/:slug/run` makes `lib/contribution-runner.js` spawn `../<slug>/run.sh` with the user's `W4H_API_KEY`, `W4H_API_BASE` and `W4H_DATASET_ID`. Stdout lines `@@PROGRESS@@ {json}` drive the progress bar.
3. **SQL analytics (ADR-023):** `lib/sql-contribution-engine.js` reads `../<slug>/manifest.yaml` and `sql/`, binds identifiers from `w4h.tables`, and runs in-process. There is no free-SQL endpoint.
4. **Extensions:** the operator installs `fft_approximate` on their Postgres; notebooks call it directly.

**Layout:** clone every repo as a sibling in one folder. The API finds contributions at `../<slug>` (override `CONTRIBUTION_RUNNER_REPO_ROOT`) and docs at `DOCS_REPO_PATH=../w4h-docs`.

**Cross-repo changes:** `w4h-api` first (regenerate `API_INDEX.md`), then `w4h-app`, then `w4h-docs`. Catalog rows are seeded in `w4h-api/data/schema.sql`. Start at `w4h-docs/dev/mvp.md` and `w4h-docs/dev/ADR-README.md` for decisions, and `w4h-docs/dev/developer-setup.md` for local setup, getting an API key, test personas, troubleshooting, per-repo test commands, default branches and a glossary. Do not commit or push unless asked; never commit `.env` files, API keys or participant data.

<!-- END w4h-system-overview -->
