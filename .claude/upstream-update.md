# Upstream Doctrine Update

**Source**: [utils](/home/jhutchison/projects/github/utils) — shared workflow template
**Action**: Review changes below and selectively merge into your project's command files.
**Cleanup**: Delete this file after reviewing.

---

## 2026-03-26: Decision Science Module — Partially Adopted

**Reviewed**: 2026-04-04.
- `decision_science` Python module: **SKIP** — Paperboy's scoring is a 2-criteria weighted sum (~30 lines). The MAUT framework is overkill. Revisit if scoring grows to 5+ criteria.
- `decision-scientist` agent: **ADAPT** — Adopted as advisory auditor for weight validity, scoring fairness, and statistical soundness. Adapted with paperboy-specific context (selector weights, keyword scoring, thresholds).
- `decision-science` team template: **SKIP** — No dedicated team needed. Agent joins existing teams as a reviewer alongside code-reviewer when DS concerns arise.

---

## 2026-03-31: Session-Start — Add Git Sync — APPLIED

**Applied**: 2026-04-04. Added `git fetch && git pull` to session-start Step 4.

---
