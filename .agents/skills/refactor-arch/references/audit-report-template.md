# Audit Report Template

Use this structure for Phase 2.

```markdown
# Architecture Audit Report: <project-name>

## Summary

| Item | Value |
| --- | --- |
| Project | <project-name> |
| Stack | <language/framework/database> |
| Scope | <files/directories analyzed> |
| Approx. LOC | <line count> |

## Severity Counts

| Severity | Count |
| --- | ---: |
| CRITICAL | <n> |
| HIGH | <n> |
| MEDIUM | <n> |
| LOW | <n> |

## Findings

### [SEVERITY] Finding Title
File: path/to/file.ext:start-end  
Category: Architecture | Security | Reliability | Performance | Maintainability  
Description: What is wrong, grounded in the code.  
Impact: Why this matters.  
Recommendation: What should change.  
MVC Target: Model | View/Route | Controller | Config | Middleware | Composition Root | Service | Helper

## Proposed Refactoring Plan

1. <first incremental change>
2. <second incremental change>
3. <third incremental change>

## Validation Plan

- <boot/import command>
- <test/lint command if available>
- <endpoint smoke check strategy>
```

Rules:

- Order findings by severity: CRITICAL, HIGH, MEDIUM, LOW.
- Include exact file paths and line numbers.
- Do not include unsupported claims.
- Include deprecated API findings when detected.
- Keep recommendations actionable enough for Phase 3.
