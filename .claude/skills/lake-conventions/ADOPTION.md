# Adopting `lake-conventions`

For a repo that reads from or writes to the lake, or a personal repo that
writes to home storage. Once per repo. Steps 1 to 3 apply to both audiences;
steps 4 and 5 are lake-only; step 6 is home-storage-only.

## 1. Copy the skill

```bash
cp -r <hub>/.claude/skills/lake-conventions .claude/skills/
diff -r <hub>/.claude/skills/lake-conventions .claude/skills/lake-conventions && echo identical
```

Level 0: copy whole, never edit locally. Route fixes upstream so the next repo
gets them. A local edit is drift with a good excuse.

## 2. Point something at it

A skill nothing references is a skill nobody loads. Add a line to `CLAUDE.md`
naming the skill and the reference repo:

> Data going to or coming from the lake or home storage follows
> `.claude/skills/lake-conventions/`. For the lake, the authoritative source is
> the `dis-lakehouse` repo, on work machines at the path in
> `config/project.yaml` under `machines.<host>.references.lakehouse`. For home
> storage there is no reference repo; `HOME-STORAGE.md` and each machine's
> local topology doc are the doctrine.

Then add it to the repo's `CONTEXT.md` Reading Order.

## 3. Add the machine roster, if the repo has none

`config/project.yaml` needs a `machines:` block so the preflight can find the
reference repo. See the hub's, and add only the hosts this repo is cloned on.
No usernames.

## 4. Copy the preflight, if the repo writes to the lake

```bash
cp <hub>/scripts/lake_preflight.py scripts/
cp <hub>/tests/unit/test_lake_preflight.py tests/unit/
pytest tests/unit/test_lake_preflight.py
```

It imports `resolve_machine` from the repo's own package. Fix that import to
match the local package name; nothing else is repo-specific.

Skip this step for a read-only consumer. A preflight nobody runs is worse than
none, because it looks like coverage.

## 5. Run it once and read the output

```bash
python scripts/lake_preflight.py --target dev
```

**Expect a nonzero first result.** Most repos are missing credentials in the
shell, or have never declared their legs. Read every line before wiring it into
anything. Do not add a check whose output you have not read.

## 6. Home storage, for personal repos only

Gate first: `HOME-STORAGE.md` opens with two checks (project scope and
machine scope). If either fails, stop here.

1. Declare the project's scope in `config/project.yaml`:

   ```yaml
   project:
     scope: personal
   ```

2. Add the role-named variables to `.env.example` with placeholder values
   (`HOME_MEDIA_ROOT=\\<nas-host>\<share>`), and the real values to `.env`
   on each machine. Never a real address anywhere committed, including
   variable names that embed a hostname.

3. If this machine has a local topology doc, point the roster at it:
   `machines.<host>.references.home_storage: <local path>`. If it does not,
   skip this; do not invent one to satisfy the field.

Skip the preflight for home storage; it checks nothing about it.

## Rollback

Delete `.claude/skills/lake-conventions/`, `scripts/lake_preflight.py`, and its
test; drop the `CLAUDE.md` and `CONTEXT.md` lines. For home-storage adopters,
also drop `project.scope`, the `HOME_*` lines in `.env.example`, and the
`references.home_storage` roster line. Nothing else depends on them.
The `machines:` block can stay; it is useful on its own.
