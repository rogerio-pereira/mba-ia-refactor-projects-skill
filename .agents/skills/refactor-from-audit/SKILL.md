---
name: refactor-from-audit
description: Language- and framework-agnostic refactoring workflow for implementing changes from a Markdown audit report. Use when Codex must read a report section named `Findings` and `Proposed Refactoring Plan`, apply each listed change one at a time, update the Markdown by prefixing completed sections with `[FIXED]`, validate each change, and create an English git commit for every fixed section.
---

# Refactor From Audit

## Purpose

Use this skill to turn a Markdown audit report into incremental code changes. The skill is language- and framework-agnostic: infer the stack, conventions, commands, tests, and formatting tools from the target repository.

The report must contain:

- A `Findings` section with actionable findings.
- A `Proposed Refactoring Plan` section with ordered or bulleted changes.

## Operating Rules

- Treat the Markdown report as the source of truth for the requested work.
- Implement one change at a time. Do not batch unrelated findings into one edit.
- Preserve public behavior unless the report or user explicitly approves a breaking change.
- Keep edits small, reversible, and aligned with the codebase's existing style.
- Do not fabricate missing requirements. If a finding or plan item is ambiguous, inspect the referenced code first and choose the smallest defensible fix.
- Do not mark anything as fixed until code is changed, validation is run, and the result is reviewed.
- After each completed change, update the same Markdown report by prefixing the completed finding or plan item heading/list item with `[FIXED]`.
- Create one git commit per fixed section, with an English commit message explaining the change.
- Never revert user changes or unrelated work.

## Markdown Parsing

1. Locate the report path from the user request. If no path is provided, search likely report locations such as `docs/reports/**/*.md`.
2. Read only the relevant report sections first:
   - `Findings`
   - `Proposed Refactoring Plan`
3. Build a work queue from unfixed entries:
   - Finding headings such as `### [HIGH] Title`.
   - Plan items such as `1. Change...` or `- Change...`.
4. Skip any entry already prefixed with `[FIXED]`, for example:
   - `### [FIXED] [HIGH] Title`
   - `1. [FIXED] Change...`
   - `[FIXED] Change...`
5. Prefer the highest severity findings first when severity is present. Otherwise, follow report order.
6. Use plan items to guide implementation order when they clearly group multiple findings.

## Per-Change Workflow

For each unfixed finding or plan item:

1. Inspect the referenced files, line numbers, tests, dependency manifests, and boot commands.
2. Define the smallest coherent implementation scope for that one entry.
3. Edit code using the repository's existing patterns and appropriate tools.
4. Run the strongest practical validation for the changed scope:
   - Existing focused tests first.
   - Existing lint/typecheck/format commands when defined.
   - Boot/import/smoke checks when tests are absent.
5. If validation fails, fix the issue and rerun validation when feasible.
6. Update the Markdown report:
   - Prefix the completed entry with `[FIXED]`.
   - Add a short completion note under the entry when useful, including validation command and result.
7. Review `git diff` to ensure only intended files changed.
8. Commit the code and report update together.

## Commit Requirements

Commit after every completed section marked `[FIXED]`.

Use English commit messages:

- `Fix SQL injection in product queries`
- `Move Flask secrets to environment config`
- `Remove unsafe admin query endpoint`
- `Refactor order loading to avoid N+1 queries`

The commit must include:

- The implementation files changed for the fix.
- The Markdown report update that marks the section as `[FIXED]`.

Do not commit .env files, unrelated files, generated caches, local databases, dependency folders, or user changes outside the fix scope.

## Report Update Rules

Use the smallest stable Markdown edit.

For a finding heading:

```markdown
### [FIXED] [CRITICAL] SQL Injection Through String-Concatenated Queries
```

For a numbered plan item:

```markdown
1. [FIXED] Replace every concatenated SQL statement with parameterized queries.
```

For a non-numbered plan item:

```markdown
[FIXED] [HIGH] Replace every concatenated SQL statement with parameterized queries.
```

Optional completion note:

```markdown
Fixed in commit `<short-sha>`.
Validation: `pytest tests/test_products.py` passed.
```

If a finding is partially addressed, do not mark it `[FIXED]`. Add a note explaining the remaining blocker and leave the heading unchanged.

## Validation Strategy

Infer commands from repository files:

- JavaScript/TypeScript: `package.json`, lockfiles, framework scripts.
- Python: `pyproject.toml`, `requirements.txt`, `pytest.ini`, `tox.ini`, `manage.py`, Flask/FastAPI/Django entry points.
- PHP: `composer.json`, framework CLIs, PHPUnit config.
- Java/Kotlin: Maven/Gradle files.
- Go: `go.mod`.
- Rust: `Cargo.toml`.
- Ruby: `Gemfile`, Rails/Rake files.
- .NET: `.sln`, `.csproj`.

When no automated tests exist, use the narrowest reliable smoke check, such as importing the app, compiling sources, starting the service briefly, or exercising unchanged public endpoints.

If validation cannot run because dependencies or services are missing, record the exact blocker in the final response and in the report note only when it affects the fixed entry.

## Final Response

End with:

- Report path updated.
- Sections fixed and commit hashes.
- Validation commands and results.
- Remaining unfixed sections or blockers.
