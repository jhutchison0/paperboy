#!/bin/bash
# PostToolUse audit for shift-left-testing discipline.
#
# Fires after every Write or Edit tool call. Never blocks the tool call.
# Logs evidence of test-partner presence for new production code in src/.
# See .claude/skills/shift-left-testing/ENFORCEMENT.md for rationale and gradient.
#
# Invariant: this script MUST exit 0 in all paths. A non-zero exit is interpreted
# by the harness as a hook failure, which can suppress or fail the tool call —
# the opposite of the soft-deterministic stance we want.

set -uo pipefail  # NOT -e: we never want a transient grep/find failure to exit non-zero.

input=$(cat 2>/dev/null || true)

# jq is the cleanest way to parse the hook input. If unavailable, exit silently
# (the audit is best-effort; missing jq should not break tool calls).
if ! command -v jq >/dev/null 2>&1; then
    exit 0
fi

tool_name=$(echo "$input" | jq -r '.tool_name // empty' 2>/dev/null)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty' 2>/dev/null)

# Only Write and Edit are audited; everything else (Read, Bash, Grep, ...) is a no-op.
case "$tool_name" in
    Write|Edit) ;;
    *) exit 0 ;;
esac

# Normalize Windows backslash paths to forward slashes so the case globs
# match on both Git Bash (Windows) and POSIX shells. The harness passes
# file_path verbatim from the tool call; on Windows that is backslash-
# separated. Without normalization, the `*/src/*.py` glob below
# would never match a Windows path and the hook would silently no-op.
file_path=${file_path//\\//}

# Only files directly under src/ are audited (paperboy uses a flat src/ layout —
# no src/<pkg>/ subdirectory). Other paths (docs/, config/, tests/ themselves,
# .claude/, scripts/) are out of scope — they don't need a test partner.
case "$file_path" in
    */src/*.py) ;;
    *) exit 0 ;;
esac

basename=$(basename "$file_path")

# Skip Python package plumbing and test discovery files.
case "$basename" in
    __init__.py|conftest.py) exit 0 ;;
esac

# Skip files that are themselves tests (in case src/ ever contains test helpers).
case "$basename" in
    test_*.py|*_test.py) exit 0 ;;
esac

# Resolve project root from the edited file's directory.
project_root=$(cd "$(dirname "$file_path")" 2>/dev/null && git rev-parse --show-toplevel 2>/dev/null)
if [ -z "${project_root:-}" ]; then
    exit 0
fi

audit_dir="$project_root/.claude/audits"
audit_log="$audit_dir/shift-left-violations.log"
mkdir -p "$audit_dir" 2>/dev/null
timestamp=$(date -Iseconds 2>/dev/null || date)

module_basename="${basename%.py}"

# Look for a test partner anywhere under tests/. Convention is
# tests/**/test_<basename>.py.
test_partners=$(find "$project_root/tests" -name "test_${module_basename}.py" 2>/dev/null)

# Second check: a test file that imports the module counts as a partner even
# when it is named by feature rather than by module (tests/test_pipeline.py
# exercising src.config, for example). Without this, feature-named suites log
# MISSING_TEST for every edit to a shared module: 27 false positives in one
# downstream wave (stx-server, 2026-08-26, commit 62f20a1). Paperboy imports
# its flat modules as src.<module>, so the dotted name keeps the src prefix.
if [ -z "$test_partners" ]; then
    module_rel="${file_path#"$project_root"/}"        # src/machine.py
    [ "$module_rel" = "$file_path" ] && module_rel="src/${file_path#*/src/}"   # path not under the root as git spells it
    module_dotted="${module_rel%.py}"
    module_dotted="${module_dotted//\//.}"           # src.machine
    module_parent="${module_dotted%.*}"               # src
    module_leaf="${module_dotted##*.}"                # machine
    module_re="${module_dotted//./\\.}"                # dots are literal in the ERE below
    parent_re="${module_parent//./\\.}"
    test_partners=$(grep -rlE \
        "^(from ${module_re} import|import ${module_re}([^a-zA-Z0-9_]|$)|from ${parent_re} import (.*[^a-zA-Z0-9_])?${module_leaf}([^a-zA-Z0-9_]|$))" \
        "$project_root/tests" --include='test_*.py' 2>/dev/null || true)
fi

if [ -z "$test_partners" ]; then
    echo "[$timestamp] MISSING_TEST file=$file_path expected=tests/**/test_${module_basename}.py" >> "$audit_log"
    cat >&2 <<EOF
[shift-left-audit] No test partner found for $file_path.
  Expected: tests/**/test_${module_basename}.py
  Vertical-slice TDD says: write a failing test first, then minimum impl to pass it.
  See .claude/skills/shift-left-testing/VERTICAL-SLICING.md
  Log: .claude/audits/shift-left-violations.log
EOF
else
    while IFS= read -r tp; do
        [ -n "$tp" ] && echo "[$timestamp] OK_TEST_EXISTS file=$file_path partner=$tp" >> "$audit_log"
    done <<< "$test_partners"
fi

exit 0
