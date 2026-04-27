# Anti-Pattern Catalog

## CRITICAL

### Hardcoded Secrets or Unsafe Defaults
- Signals: literal `SECRET_KEY`, passwords, tokens, API keys, default admin credentials, production debug defaults.
- Impact: exposes sensitive configuration and weakens production safety.
- Remediation: move values to environment-aware config and provide `.env.example` placeholders.

### SQL Injection or Unsafe Query Construction
- Signals: SQL built with string concatenation, f-strings, template literals, `%` interpolation, or user input embedded directly.
- Impact: allows data exfiltration, mutation, or authentication bypass.
- Remediation: use parameterized queries or ORM filters.

### Unauthenticated Administrative or Destructive Endpoints
- Signals: routes that run arbitrary SQL, delete data, expose reports, reset state, or return sensitive records without auth/authorization.
- Impact: permits destructive actions or sensitive data exposure.
- Remediation: remove the endpoint or protect it with authentication, authorization, and audit logging.

### God File, God Class, or God Method
- Signals: one file/class handles boot, routes, database, validation, business logic, serialization, and reporting.
- Impact: makes behavior hard to test, reason about, and safely change.
- Remediation: split by MVC responsibility and domain.

## HIGH

### Business Logic Embedded in Routes
- Signals: route handlers calculate totals, enforce workflows, mutate many entities, send notifications, or decide domain outcomes.
- Impact: controllers/routes become untestable and duplicated.
- Remediation: move use-case flow to controllers or services.

### Data Access Embedded in Routes or Controllers
- Signals: route handlers open connections, write SQL, call ORM sessions directly for complex queries.
- Impact: couples HTTP handling to persistence details.
- Remediation: extract model/repository boundaries.

### Tight Coupling and Hidden Dependencies
- Signals: modules instantiate concrete dependencies internally, rely on mutable globals, or import app/session singletons everywhere.
- Impact: prevents isolated tests and controlled composition.
- Remediation: introduce a composition root and pass dependencies explicitly.

### Sensitive Data Exposure
- Signals: password hashes, tokens, internal errors, stack traces, or private fields returned in API responses.
- Impact: leaks confidential or implementation details.
- Remediation: centralize serializers and redact private fields.

## MEDIUM

### Missing or Inconsistent Validation
- Signals: ad hoc `if` checks in routes, missing type checks, inconsistent required fields.
- Impact: accepts invalid data and creates unpredictable behavior.
- Remediation: centralize request validation per endpoint/use case.

### Inconsistent Error Handling
- Signals: mixed response shapes, repeated try/catch blocks, raw exception messages, inconsistent status codes.
- Impact: makes clients and support workflows unreliable.
- Remediation: centralize error classes and error middleware/handlers.

### Duplicated Business Rules or Serialization
- Signals: repeated response mapping, repeated total calculations, repeated validation snippets.
- Impact: changes drift across endpoints.
- Remediation: extract service, helper, or serializer functions.

### N+1 Queries or Repeated I/O in Loops
- Signals: database calls inside loops, per-row loading of related records.
- Impact: degrades performance as data grows.
- Remediation: batch queries, joins, eager loading, or repository methods.

### Deprecated Framework or Library APIs
- Signals: APIs marked legacy by the framework, such as SQLAlchemy `Query.get()` instead of `Session.get()`.
- Impact: creates upgrade risk and warnings.
- Remediation: replace with the supported modern API.

## LOW

### Poor Naming or Unclear Function Boundaries
- Signals: vague names, functions doing unrelated tasks, unclear variable intent.
- Impact: slows maintenance.
- Remediation: rename and split small helpers where useful.

### Magic Numbers or Strings
- Signals: repeated literal status values, limits, role names, or configuration values.
- Impact: hides business intent.
- Remediation: introduce constants or config values.

### Dead Comments or Debug Logging
- Signals: stale comments, `print`, `console.log`, commented-out code.
- Impact: reduces readability and signal.
- Remediation: remove dead code or use structured logging.
