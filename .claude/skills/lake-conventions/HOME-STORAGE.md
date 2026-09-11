# Home storage: the personal side

The lake serves work. A personal project's bulk data goes to home storage
instead: a network-attached storage device on the home LAN, reached over SMB.
This file is the portable half of that arrangement. Every hostname, share
name, pool name, and drive path stays out of git; the sections below say
where each one lives instead.

## Does this file apply?

Two checks, both required:

1. **The project is personal.** `config/project.yaml` declares it:

   ```yaml
   project:
     scope: personal
   ```

   An absent `scope` means `work`. A work project follows lake doctrine even
   on a machine that could reach home storage; the project's nature decides,
   not the box's capability.

2. **The machine is in the roster with `personal` in its scope, and
   `known` is true.** An unknown machine is not a personal machine. The
   `unknown` roster entry carries personal scope so resolution never errors,
   but that default does not open this gate: add the box to `machines:`
   first.

A personal project on a machine without personal scope is a misconfiguration.
Say so and stop. Do not fall back to the lake, a local directory, or a guess.

**The routing rule, in one sentence**: the project's scope selects the
storage system; work-scoped data goes to the lake, personal-scoped data goes
to home storage, and crossing that line is a human decision made explicitly,
never a fallback or a convenience.

## Where the real paths live

Three tiers, strictly separated:

| Tier | Holds | Lives |
|---|---|---|
| Doctrine | Rules, hazards, naming conventions | This file, committed |
| Runtime scalars | One data-root path per role | `.env`, per machine, never committed |
| Topology | Which shares exist, layout, snapshot schedule | A machine-local doc, outside git |

The boundary line, stated once so it can be checked: **committed config may
point at code and docs (tilde-relative, no usernames); only the environment
points at data. Anything that resolves over a network (a UNC path, a
hostname, an IP, a mount endpoint) never goes in git, in any file, in any
role.**

- Variables are named for the data's role, never for a host or a deployment
  codename: `HOME_MEDIA_ROOT`, `HOME_CORPUS_ROOT`, `HOME_STORES_ROOT`. A
  committed variable name containing a hostname is half an address in git,
  and names get committed even when values do not. `.env.example` carries
  the names with placeholder values; only `.env` knows the real ones.
- `.env` is the single home for the values. Not the shell profile, not a
  config YAML, not a module constant. Two blessed locations produce machines
  holding both, disagreeing.
- The topology narrative (the local doc naming real shares, layouts, and
  snapshot schedules) stays outside every repo, or inside one only under a
  `.gitignore` path the adopting repo has verified covers it. Point the
  roster at it per machine: `machines.<host>.references.home_storage:
  <local path>`. A docs pointer passes the boundary line; a data root in the
  roster does not.

**There is no authoritative reference repo for home storage.** The lake has
`dis-lakehouse`; the personal side has only this file and each machine's
local topology doc. Never cite a gitignored hub file from committed text; on
every other machine it is a dangling pointer.

## One device, three address forms

The same storage answers to three forms. Use the right one for the context.

| Form | Shape | Who uses it |
|---|---|---|
| Server-side path | a mount path on the device | The device itself: its config, apps on the box, direct sessions |
| Client network path | `\\<nas-host>\<share>` | Every consumer machine: file managers, sync tools, application code |
| Admin UI | a browser URL | Humans configuring shares. No data flows here |

Client code never uses the server-side path. If a script contains a
server-side mount path and does not run on the device, it is wrong. The same
environment variable makes this portable: on a client it holds the network
path, on the device it holds the server path, and the code does not change.

## The code pattern: required variable, loud failure

```python
import os
from pathlib import Path

try:
    MEDIA_ROOT = Path(os.environ["HOME_MEDIA_ROOT"])
except KeyError as exc:
    raise RuntimeError(
        "HOME_MEDIA_ROOT is not set. Home-storage roots live in .env on "
        "each machine, never in code or committed config."
    ) from exc
```

No default, ever. A default is either a real address in git or a guess at
one. The first breaks the boundary line; the second reaches for a host that
may not exist and buys a slow SMB timeout in place of a clear message. This
is the lake's own rule in home clothes: a bare invocation is an error, not
production.

## Six rules that were paid for

1. **Never run an embedded database against a network share.** SQLite,
   DuckDB, Kuzu, on-disk vector stores: file locking over SMB corrupts.
   Live stores stay local with the compute; the device holds closed copies,
   taken after the database is shut or from a snapshot.
2. **A mirror with deletions is availability, not backup.** A mirroring sync
   faithfully replicates a mistake, deletions included. The device's
   snapshot schedule, or a genuinely offline copy, is the undo.
3. **Redundancy survives hardware, not operators.** Single-parity RAID
   survives one drive failure; it does not survive a mirrored deletion.
   Rule 2 again, seen from the disk side.
4. **Address the device by name, never by IP.** A DHCP reservation makes an
   IP stable enough for today; a name survives re-addressing and device
   replacement.
5. **Data access uses a least-privilege account.** The admin account
   configures the device and never mounts client shares. Cache the
   credential through the OS credential store, not in a script and not in
   `.env`.
6. **Bulk data lives on the device; compute and working copies stay local.**
   New bulk data goes to home storage, the workstation processes it, and
   nothing gates on a working copy another machine cannot see.

## Companion files, lighter

The lake's contract (a `README.md` and a schema-validated `manifest.json`
beside every dataset) exists for governed, multi-team, queryable storage.
Home storage carries it lighter:

- **Bulk media mirrors**: no companion files. A mirror of a local tree is
  self-describing, and per-folder ceremony will not be maintained.
- **Derived and replicated datasets** (a source corpus, database replicas,
  kept artifacts): a `README.md` beside each one, saying what it is a copy
  of, as of when, and whether it is safe to treat as current. Skip the
  machine-readable manifest; no upstream schema exists to validate against,
  and inventing one for a single deployment is speculative.

A layout that separates a corpus of record, store replicas, and kept
artifacts has worked well. Treat that as an example shape, not a mandate;
the actual share and directory names are addresses and live with the
machine, not the doctrine.

## What this file does not cover

- **`scripts/lake_preflight.py` checks nothing about home storage.** A green
  preflight says nothing about it. No home-storage preflight exists yet, and
  none should be built until a real run defines what it must mirror
  (`PREFLIGHT.md`: a conservative gate is still a wrong gate).
- **Machine-local operations**: share creation, mirror-job invocations,
  credential-caching steps, admin procedures, and the actual share and
  directory names. Those live in the machine's topology doc, beside the
  addresses they depend on.
