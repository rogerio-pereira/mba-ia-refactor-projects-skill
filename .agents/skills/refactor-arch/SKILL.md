---
name: refactor-arch
description: Analyze any backend codebase, audit architecture/code-quality issues, generate a severity-ranked report, and refactor toward MVC after explicit confirmation.
---

# Refactor Arch

## Purpose

Use this skill to transform a legacy or partially organized backend project into a maintainable MVC architecture. The workflow is technology-agnostic and must adapt to Python/Flask, Node.js/Express, or another stack inferred from the target project.

The skill always runs in three phases:

1. **Project Analysis**: detect language, framework, dependencies, database, domain, entry points, routes, and current architecture.
2. **Architecture Audit**: inspect the code against the anti-pattern catalog, generate a structured report with exact file/line findings, and pause for human confirmation.
3. **MVC Refactoring and Validation**: after approval, apply the report plan incrementally, validate behavior, update the report, and preserve the public API.

## Reference Files

Load only the references needed for the current phase:

- `references/project-analysis.md`: stack, dependency, route, database, and architecture detection heuristics.
- `references/antipattern-catalog.md`: anti-patterns, severities, detection signals, impact, and remediation.
- `references/audit-report-template.md`: required Phase 2 report structure.
- `references/mvc-guidelines.md`: target MVC responsibilities and boundaries.
- `references/refactoring-playbook.md`: concrete before/after transformation patterns.

If any reference is missing, continue with this `SKILL.md` and report the missing file as a skill improvement item.

## Operating Rules

- Work from the project where the skill is invoked. If no target is specified, use the current working directory.
- Do not modify files during Phase 1 or Phase 2.
- Never fabricate findings. Every finding must include an exact file path and line number or line range.
- Phase 2 must stop and ask exactly: `Phase 2 complete. Proceed with MVC refactoring (Phase 3)? [y/n]`
- Do not start Phase 3 until the user answers yes.
- During Phase 3, implement one finding or plan item at a time.
- Preserve route paths, HTTP methods, response schemas, status codes, seed data, and startup behavior unless the user explicitly approves a breaking change.
- Prefer the conventions already used by the detected framework.
- Keep secrets in environment variables and `.env.example` placeholders. Do not commit real `.env` files.
- Validate after each coherent change with the strongest practical command available in the project.

## Phase 1: Project Analysis

Read `references/project-analysis.md`, inspect the target project, and print:

```markdown
## Phase 1: Project Analysis

| Item | Analysis |
| --- | --- |
| Language | <detected language and version when available> |
| Framework | <detected framework and version when available> |
| Dependencies | <key runtime dependencies> |
| Domain | <inferred application domain> |
| Architecture | <current structure and main violations> |
| Source files | <count and scope analyzed> |
| Entry point | <main boot file or command> |
| Routes | <route modules or inferred endpoint list> |
| Database | <database/client/ORM/files when detectable> |
```

## Phase 2: Architecture Audit

Read `references/antipattern-catalog.md`, `references/audit-report-template.md`, and `references/mvc-guidelines.md`.

Generate a Markdown audit report with:

- Project name, stack, analyzed scope, and approximate lines of code.
- Summary counts by severity.
- Findings ordered by severity: CRITICAL, HIGH, MEDIUM, LOW.
- At least 5 findings when the codebase contains enough issues.
- At least one CRITICAL or HIGH finding when present.
- Exact file and line references for every finding.
- Impact, actionable recommendation, and MVC target for every finding.
- Deprecated API detection when applicable.
- A proposed Phase 3 refactoring plan.

Save the report when the user provides a path. Otherwise print it and recommend `reports/audit-project-N.md`.

After the report, stop and ask:

```markdown
Phase 2 complete. Proceed with MVC refactoring (Phase 3)? [y/n]
```

## Phase 3: MVC Refactoring and Validation

Read `references/refactoring-playbook.md` and `references/mvc-guidelines.md`. Use the saved report as the source of truth.

For each unfixed finding or plan item:

1. Inspect the referenced files and line numbers.
2. Define the smallest coherent implementation scope.
3. Edit code following the target project's framework conventions.
4. Validate with focused tests, lint/typecheck, import/boot checks, or endpoint smoke checks.
5. Update the report by prefixing the completed heading or list item with `[FIXED]`.
6. Commit the implementation and report update with an English commit message.

Required completion output:

```markdown
## Phase 3: Refactoring Complete

### New Project Structure
<summarize MVC directories and entry point>

### Validation
- <pass/fail> Application boots without errors
- <pass/fail> Original endpoints respond correctly or route compatibility was verified
- <pass/fail> Tests/lint executed when available
- <pass/fail> Remaining high-risk anti-patterns reviewed
```

If validation fails, diagnose and fix it when feasible. If the current environment cannot run validation, report the exact command, blocker, and residual risk.

## Severity Scale

- **CRITICAL**: severe architecture or security failures that can break correct behavior, expose sensitive data, or completely violate separation of responsibilities.
- **HIGH**: strong MVC or SOLID violations that make maintenance and testing difficult.
- **MEDIUM**: standardization, duplication, validation, or performance issues.
- **LOW**: readability and maintainability issues.

## Final Response

End with:

- Files changed.
- Report path updated.
- Sections fixed and commit hashes created.
- Validation commands and results.
- Any unresolved risks or manual follow-up.
