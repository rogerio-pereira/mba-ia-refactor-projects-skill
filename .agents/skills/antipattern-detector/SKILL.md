---
name: refactor-arch
description: Analyze any codebase, audit architecture/code quality issues, produce severity-ranked findings, refactor toward MVC, and validate behavior after changes.
---

# Architecture Audit and MVC Refactoring Skill

## Purpose

Use this skill to transform a legacy or partially organized project into a maintainable MVC architecture. The skill is technology-agnostic.

The skill runs in three sequential phases:

1. **Project Analysis**: detect stack, domain, dependencies, architecture, source layout, and execution commands.
2. **Architecture Audit**: inspect the code against an anti-pattern catalog, generate a structured report with exact file/line findings, then pause for human confirmation.
3. **MVC Refactoring and Validation**: apply the approved refactor, preserve behavior, and validate boot plus endpoint compatibility.

## Operating Rules

- Work from the target project the user asks you to analyze. If no target is specified, use the current working directory.
- Be technology-agnostic: infer language, framework, database, package manager, and test/boot commands from project files.
- Do not modify files during Phase 1 or Phase 2.
- Phase 2 must pause and ask for explicit confirmation before Phase 3.
- During Phase 3, keep behavior compatible with the original public API unless the user explicitly approves a breaking change.
- Prefer small, reversible edits that follow the project's existing framework conventions.
- Never fabricate findings. Every finding must include an exact file path and line number or line range.
- Do not assume missing context. If a necessary command, endpoint list, or runtime prerequisite cannot be inferred, state the uncertainty and choose the safest validation path.

## Required Reference Knowledge

When bundled reference files are available, load only the relevant files as needed. The skill should be supported by Markdown references covering these five areas:

- **Project analysis heuristics**: how to detect language, framework, dependencies, database, domain, entry points, routes, and current architecture.
- **Anti-pattern catalog**: at least 8 detectable anti-patterns with severity, signals, impact, and remediation guidance.
- **Audit report template**: the exact structure used in Phase 2.
- **MVC architecture guidelines**: responsibilities for Models, Views/Routes, Controllers, configuration, middleware, and composition root.
- **Refactoring playbook**: at least 8 concrete before/after transformation patterns, including examples.

If a required reference file is missing, continue using the rules in this SKILL.md and report the missing reference as a skill improvement item.

## Severity Scale

Classify findings with this scale:

- **CRITICAL**: severe architecture or security failures that can break correct behavior, expose sensitive data, or completely violate separation of responsibilities. Examples: hardcoded secrets, SQL injection, a god file/class that mixes routing, persistence, validation, and business logic.
- **HIGH**: strong MVC or SOLID violations that make maintenance and testing difficult. Examples: heavy business logic inside controllers/routes, tight coupling with no dependency injection boundary, mutable global state shared across the app.
- **MEDIUM**: standardization, duplication, validation, or performance issues. Examples: N+1 queries, missing route/input validation, inconsistent error handling, repeated logic across endpoints.
- **LOW**: readability and maintainability issues. Examples: poor naming, magic numbers, unclear function boundaries, dead comments, minor duplication.

## Minimum Anti-Pattern Coverage

The audit must check for at least these categories:

- Hardcoded secrets, credentials, tokens, or unsafe configuration defaults.
- SQL injection or unsafe command/query construction.
- God files, god classes, or god methods.
- Business logic embedded in routes/controllers.
- Data access embedded in routes/controllers instead of models/repositories.
- Missing validation or inconsistent request parsing.
- Inconsistent or duplicated error handling.
- Tight coupling, hidden dependencies, or uncontrolled global mutable state.
- Repeated business rules or duplicated query/serialization code.
- Deprecated framework/library APIs and their modern replacements.
- N+1 queries or avoidable repeated I/O inside loops.
- Missing composition root or unclear application entry point.
- Duplicated logic that can be reused through shared services, helpers, or model methods.

## Phase 1: Project Analysis

Inspect project metadata and source files to produce a concise analysis summary.

Required output:

```text
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <detected language and version when available>
Framework:     <detected framework and version when available>
Dependencies:  <key runtime dependencies>
Domain:        <inferred application domain>
Architecture:  <current structure and main violations>
Source files:  <count and scope analyzed>
Entry point:   <main boot file or command>
Routes:        <route modules or inferred endpoint list>
Database:      <database/client/ORM/files when detectable>
================================
```

Detection guidance:

- Language signals: dependency manifests, lockfiles, build files, source file extensions, shebangs, compiler/interpreter settings, container files, and CI commands.
- Framework signals: declared dependencies, imports/includes, application factory or bootstrap calls, route/controller declarations, middleware hooks, dependency injection containers, and framework-specific configuration files.
- Runtime signals: documented start commands, package scripts, task runners, process managers, container entrypoints, environment files, and test commands.
- Persistence signals: database drivers, ORM/query builder usage, migration folders, schema files, connection factories, repository/model modules, and raw query construction.
- Architecture signals: folder/module names, import or dependency graph, request flow, routing boundaries, model/repository boundaries, controller/service boundaries, config loading, middleware, tests, and startup composition.

## Phase 2: Architecture Audit

Scan the codebase against the anti-pattern catalog and produce a Markdown report. The report must be saved when the user provides a target path; otherwise print it and recommend `docs/reports/audit-project-N.md`.

The report must include:

- Project name, stack, analyzed scope, and approximate lines of code.
- Summary counts by severity.
- Findings ordered by severity: CRITICAL, HIGH, MEDIUM, LOW.
- At least 5 findings when the codebase contains enough issues.
- At least one CRITICAL or HIGH finding when present.
- Exact file and line references for every finding.
- Impact and actionable recommendation for every finding.
- Deprecated API detection when applicable.
- A proposed Phase 3 refactoring plan.

Use this finding format:

```markdown
### [SEVERITY] Finding Title
File: path/to/file.ext:start-end
Category: Architecture | Security | Reliability | Performance | Maintainability
Description: What is wrong, grounded in the code.
Impact: Why this matters.
Recommendation: What should change.
MVC Target: Model | View/Route | Controller | Config | Middleware | Composition Root | Service | Helper
```

After the report, stop and ask:

```text
Phase 2 complete. Proceed with MVC refactoring (Phase 3)? [y/n]
```

Do not edit files until the user confirms.

## Phase 3: MVC Refactoring

After confirmation, refactor the project toward MVC while preserving behavior.

Target responsibilities:

- **Models**: data access, persistence objects, query helpers, domain entities, and database abstractions.
- **Views/Routes**: framework route declarations, request/response mapping, HTTP status codes, and serialization boundaries. For APIs, routes act as views.
- **Controllers**: application flow, orchestration, calls to models/services, and use-case coordination.
- **Config**: environment-based settings, secrets loading, database URLs, and runtime flags.
- **Middleware**: cross-cutting concerns such as error handling, auth checks, CORS, logging, and request context.
- **Composition root**: application creation, dependency wiring, route registration, and boot command.

Required transformation patterns:

- Extract hardcoded configuration into environment-aware config modules.
- Move database access out of routes/controllers into model or repository boundaries.
- Move business rules out of routes into controllers or services used by controllers.
- Split god files/classes into cohesive MVC modules by domain.
- Centralize request validation and error responses.
- Replace deprecated APIs with supported equivalents.
- Remove duplicated query, validation, and serialization logic.
- Introduce explicit dependencies instead of hidden mutable globals.
- Preserve route paths, HTTP methods, response schemas, and status codes unless approved.
- Keep migrations, seed data, and tests compatible with the new structure.

**IMPORTANT**
- If using a framework with strong conventions (e.g., Rails, Django, Laravel), follow the standard project structure and best practices for that framework.
- If the project already has a partial MVC structure, refactor toward a cleaner separation of concerns without necessarily creating new folders if not needed. The goal is to improve maintainability and testability,

## Validation

Validate with the strongest commands the project supports:

- Install dependencies only if needed and approved by the user/environment.
- Run formatting or linting only if the project already defines it.
- Run tests when available.
- Start or import the application to verify it boots without errors.
- Exercise original endpoints using existing API files, tests, route maps, or minimal HTTP checks.

Required validation output:

```text
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<summarize MVC directories and entry point>

## Validation
  <pass/fail> Application boots without errors
  <pass/fail> Original endpoints respond correctly or route compatibility was verified
  <pass/fail> Tests/lint executed when available
  <pass/fail> Remaining high-risk anti-patterns reviewed
================================
```

If validation fails, diagnose the failure, fix it when feasible, and rerun validation. If it cannot be fixed in the current environment, clearly report the blocker, exact failing command, and remaining risk.

## Final Response

End with:

- Files changed.
- Report path, if saved.
- Validation commands and results.
- Any unresolved risks or manual follow-up needed.
