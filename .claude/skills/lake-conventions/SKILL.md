---
name: lake-conventions
description: Conventions for the two storage systems this fleet writes to. For the work lakehouse: bucket tiers, path grammars, file formats, the two companion files every dataset ships, and the dev/prod split. For personal projects on personal-scoped machines, HOME-STORAGE.md covers writing bulk data to home network storage with no address in git. Use when adding or reviewing any code that writes to the lake or to home storage, choosing a format for a stored artifact, planning a dev-to-production promotion, or preparing a machine to do storage work.
version: "1.1.0"
---

# Lake conventions

The lake has rules. They are written down, they are not enforced by anything,
and the cost of missing one is paid by whoever reads your data next.

**Authoritative source**: the `dis-lakehouse` repo, on work machines at the path
in `config/project.yaml` under `machines.<host>.references.lakehouse`. Its
`skills/`, `templates/`, and notebook "Rules of the Road" section are the
authority. This skill is the portable mapping. **When the two disagree,
upstream wins**, and the disagreement is a bug in this file worth fixing.

Read `PREFLIGHT.md` before a first run on a new machine. Read `ADOPTION.md`
once per repo.

**Which storage system?** The project's scope selects it: work-scoped data
goes to the lake, personal-scoped data goes to home storage, and crossing
that line is a human decision made explicitly, never a fallback or a
convenience. A personal project (`project.scope: personal` in
`config/project.yaml`, on a rostered machine with `personal` scope) reads
`HOME-STORAGE.md` instead of the lake sections below. Everything below this
line is the lake.

## When to use

- Adding or reviewing code that writes to the lake
- Choosing a file format for a lake artifact
- Planning a promotion from development to production
- Auditing an existing surface for format or path drift
- Preparing a machine to do lake work (then run `scripts/lake_preflight.py`)
- Writing a personal project's bulk data to home storage (read `HOME-STORAGE.md`)

## Buckets are maturity tiers, not environments

Data is promoted between buckets. There is no dev cluster and no prod cluster.

| Bucket | What it holds | May you write? |
|---|---|---|
| `landing` | Raw external drops, byte-for-byte as received | Yes, unmodified bytes only |
| `staging` | Curated derivations. The default target for team output | Yes, this is where your work goes |
| `iceberg-warehouse` | Governed tables | **Never directly.** Iceberg commits metadata and expects consistency |
| `hive-warehouse` | Hive metastore default | **Never directly** |
| `temporary` | Scratch, purgeable without warning | Yes, and own the sweeping |

Promotion runs `landing` to `staging` to Iceberg. The Iceberg step is a
`CREATE`/`INSERT ... SELECT` through Trino over a Hive external table, or the
object registry doing it for you. Never a file copy into the warehouse prefix.

Nothing in `temporary` may be gated on by a consumer. It can vanish mid-run.

## Two path grammars

Both are in use. Pick by what the data is, not by preference.

**Product and cycle**, for human-curated deliverables:

```
s3://<bucket>/<project>/<product>/<cycle>/<team>/<filename>
```

`<cycle>` is `YYYYMMDDHH` in UTC. Sortable, and it matches the NWP convention.

**Table**, for machine-ingested tabular data:

```
s3://staging/<project>/<table>/ref_month=YYYY-MM-DD/<file>.parquet
```

Hive-style `key=value/` directories. Note the trap: **Hive tables are created
without `PARTITIONED BY` even though the data is laid out in partition
directories.** That is a deliberate workaround for a Trino bug against S3, not
an oversight. Iceberg carries the real partitioning.

Two case conventions, also both real: `snake_case` for dataset and table
identifiers (the manifest schema enforces `^[a-z0-9_]+$`), `kebab-case` for
object-key path segments in `landing`.

## Format follows audience

| Audience | Format |
|---|---|
| Tabular data for machines | **Parquet.** Mandatory in `staging` |
| Gridded scientific | NetCDF4, CF conventions preserved |
| Vector geospatial | GeoParquet preferred, GeoPackage accepted |
| Raster | Cloud-Optimized GeoTIFF |
| Provenance and config | JSON or YAML, travelling as `manifest.json` |
| Humans | `README.md` beside the data |

The mental shift, from the lakehouse's own notebooks:

> Old habit: `df.to_csv("output.csv")`, then upload somewhere.
> New habit: `df.to_parquet(buf)`, then `put_object` with a `README.md` and a
> `manifest.json` next to it.

CSV is for one-off email attachments. It carries no schema, cannot be read
columnar, and cannot be queried through Trino.

Bulk tabular data as JSON in `staging` is the anti-pattern to watch for. If you
are reaching for a JSON writer and the payload is a table of rows, stop.

## Every dataset ships two companion files

In the same prefix as the data, always:

- **`README.md`** for a human: what this is, where it came from, caveats, how
  to regenerate it.
- **`manifest.json`** for a machine, against the upstream
  `templates/manifest_schema.json` (JSON Schema draft-07). Required:
  `dataset_name`, `version`, `created_utc`, `team`, `producer{script,version}`,
  `lakehouse_path{bucket,prefix}`, `files[]{name,format,size_bytes,description}`.
  Add `upstream_sources` so lineage survives you.

They are not alternatives. One is prose, one is parseable.

The lakehouse's `.gitignore` states the doctrine in miniature: it excludes every
data extension and then negates exactly `README.md` and the manifest files. The
data goes to the lake; the description of the data goes to git.

## Three client settings, non-negotiable

Every S3 client, every language:

| Setting | Value | Why |
|---|---|---|
| Signature version | `s3v4` | required |
| Addressing style | `path` | virtual-host style is not supported |
| Region | `us-east-1` (`""` for R's `aws.s3`) | must match the credentials |

Endpoint URLs carry an explicit port. This is not AWS. The `Host` header is the
first place to look when a request signs wrong, especially behind a proxy.

Credentials arrive as an access key and secret key pair, issued on request. Two
environment-variable namespaces exist and both are load-bearing: the docs use
`MINIO_*`, several upstream operational scripts and the registry service read
`S3_*`. Set both.

## Dev and production

The split is a **named target selected explicitly at every entry point**, and
the safe default is refusing to guess.

- A bare invocation with no target is an error, not production.
- An unrecognized target name is an error. Never fall back to a base config.
- Development work writes to `temporary` under a namespace derived from `$USER`
  at runtime. Do not commit a username into config.
- **Thread the target through every process in the chain.** This is the one that
  bites. A flag honored by three processes and ignored by the fourth produces no
  error and wrong data.

`scripts/lake_preflight.py --target dev --leg "..." --leg "..."` checks the
threading before the run rather than after.

## When in doubt

1. Open the `dis-lakehouse` repo. It is the authority.
2. Find the closest row in its file-format guidance.
3. If your case fits no row, ask the lakehouse maintainers before shipping.
   Do not invent a convention quietly; a private convention is drift with a
   good excuse.

Its documentation lags its deployment. Endpoints named in its top-level docs
may describe an older host than the one its `docker/` tree now ships. Trust the
deployment tree over the prose when they disagree.

## Version History

- **1.1.0** (2026-08-30): Home-storage coverage as a new sidecar,
  `HOME-STORAGE.md`, for personal projects on personal-scoped machines.
  Harvested from a gitignored local storage doc and generalized: every
  hostname, share name, pool name, and drive path removed. Keeps the
  three-address-forms rule, roots-from-environment with a required-variable
  loud-failure pattern (no address defaults, role-named `HOME_<ROLE>_ROOT`
  variables), the embedded-database-over-SMB hazard, mirror-is-not-backup,
  address-by-name, least-privilege credentials, and bulk-data-to-device.
  `config/project.yaml` gains an optional `project.scope` field (absent
  means work); the routing paragraph above reads it alongside the machine
  roster's scope.
- **1.0.0** (2026-08-29): Initial, in the hub. Harvested from `launch-control`'s
  local `lake-conventions` 1.0.0 (2026-07-27), which covered format-by-bucket
  and the `_tmp/` scratch namespace for one repo. Generalized: repo-specific
  writers, package paths, and maintainer identity removed; bucket tiers, both
  path grammars, the companion-file contract, client settings, and the dev/prod
  section added, the last drawn from what launch-control learned by writing to
  production for five days.
