# AGENTS.md — w4h-sample-icde-demo-csv-importer

Paired importer for **w4h-sample-icde-demo-csv**. Notebook + CLI + tests.

- API key via `W4H_API_KEY` in local `.env` only — never in git.
- Do not add direct Postgres / `to_sql` paths; use the W4H API.
- Sends `table_prefix: "icde_demo"` in every import payload (see `csv_import.py`'s `TABLE_PREFIX`) — do not drop it; without it, tables would collide with other vendors' physical tables in the same dataset schema.
