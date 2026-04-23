# Architecture Audit: ecommerce-api-legacy

## Phase 1: Project Analysis

| Item | Analysis |
| --- | --- |
| Language | JavaScript running on Node.js; runtime version is not pinned in the repository |
| Framework | Express 4.18.2 |
| Dependencies | `express`, `sqlite3` |
| Domain | E-commerce/LMS checkout API for courses, enrollments, payments, administrative reporting, and user deletion |
| Architecture | The project is concentrated in a single orchestration class. `AppManager.js` owns schema creation, seed loading, routing, validation, payment flow, persistence, logging, and reporting, while `utils.js` centralizes unsafe config and mutable globals. There is no meaningful MVC separation. |
| Source files | 5 files analyzed in `ecommerce-api-legacy`, totaling 225 lines; 3 JavaScript source files plus README and API examples |
| Entry point | `ecommerce-api-legacy/src/app.js`; documented start command is `npm start` |
| Routes | `POST /api/checkout`, `GET /api/admin/financial-report`, `DELETE /api/users/:id` |
| Database | In-memory SQLite created in `ecommerce-api-legacy/src/AppManager.js:7-22`; schema and seed data are created during application bootstrap |

## Phase 2: Architecture Audit

Project: `ecommerce-api-legacy`

Stack: Node.js, Express, SQLite

Analyzed scope: `ecommerce-api-legacy/src/AppManager.js`, `ecommerce-api-legacy/src/app.js`, `ecommerce-api-legacy/src/utils.js`, `ecommerce-api-legacy/README.md`, `ecommerce-api-legacy/api.http`, `ecommerce-api-legacy/package.json`

Approximate lines of code: 225 total lines, including 180 JavaScript lines

### Summary By Severity

| Severity | Count |
| --- | ---: |
| CRITICAL | 2 |
| HIGH | 4 |
| MEDIUM | 3 |
| LOW | 1 |

## Findings

### [FIXED] [CRITICAL] Hardcoded Secrets, Plaintext Credentials, And Sensitive Data Exposure
File: `ecommerce-api-legacy/src/utils.js:1-7`, `ecommerce-api-legacy/src/AppManager.js:18`, `ecommerce-api-legacy/src/AppManager.js:45`  
Category: Security | Architecture  
Description: The codebase hardcodes database and payment credentials in `config`, seeds a user with password `123`, and logs raw card data together with `paymentGatewayKey` during checkout processing.  
Impact: Secrets are source-controlled, seeded credentials are trivially guessable, and payment/logging flows expose highly sensitive data. This is a direct confidentiality risk and a severe operational security failure.  
Recommendation: Move runtime secrets into an environment-aware config module, remove all hardcoded credentials from source, seed only non-sensitive fixtures, and never log raw card numbers or gateway keys. Create a .env and .env.example file, use current secrets in .env, make sure .env is not commited.  
MVC Target: Config  
Validation: `node -e "const { config } = require('./ecommerce-api-legacy/src/config'); ..."` passed and a boot smoke test for `src/app.js` passed after installing dependencies with `npm ci`.  

### [FIXED] [CRITICAL] God Class Mixes Bootstrapping, Routing, Business Rules, Persistence, And Reporting
File: `ecommerce-api-legacy/src/AppManager.js:1-138`  
Category: Architecture | Maintainability  
Description: `AppManager` is responsible for database connection lifecycle, schema creation, seeding, route registration, validation, checkout orchestration, payment decisions, audit logging, reporting assembly, and destructive user deletion.  
Impact: This concentration of responsibilities makes the application hard to test, hard to change safely, and incompatible with maintainable MVC boundaries. A change in one use case can easily regress unrelated areas.  
Recommendation: Split the code into a composition root plus dedicated route/controller, service, repository/model, config, and middleware modules while preserving the current HTTP contract.  
MVC Target: Composition Root  
Validation: `node -e "const { createApp } = require('./ecommerce-api-legacy/src/createApp'); ..."` passed with smoke checks for checkout, report, and delete routes.  

### [FIXED] [HIGH] Checkout Flow Uses Weak Password Hashing And Unsafe Default Password Fallback
File: `ecommerce-api-legacy/src/AppManager.js:66-71`, `ecommerce-api-legacy/src/utils.js:17-23`  
Category: Security  
Description: New users are created with `badCrypto(p || "123456")`, which silently falls back to a default password and derives a deterministic 10-character pseudo-hash from repeated Base64 fragments.  
Impact: Account creation can succeed with an implicit weak password, and stored credentials are easily predictable and unsuitable for any real authentication scenario.  
Recommendation: Require an explicit password for user creation, reject missing credentials, and replace `badCrypto` with a standard password hashing function such as `bcrypt` or `argon2`.  
MVC Target: Service  
Validation: checkout smoke test now returns `400` when `pwd` is omitted for a new user, and a database seed check confirmed the stored password is no longer `123`.  

### [FIXED] [HIGH] Checkout Workflow Lacks Transaction Boundaries And Can Leave Partial State
File: `ecommerce-api-legacy/src/AppManager.js:37-77`  
Category: Reliability  
Description: The checkout path performs multiple dependent writes across `users`, `enrollments`, `payments`, and `audit_logs` through nested callbacks without an explicit transaction or rollback strategy. The audit log insert error is ignored entirely before sending success.  
Impact: Failures in the middle of the workflow can leave orphaned or inconsistent rows, while clients still receive success responses in some error paths.  
Recommendation: Wrap the entire checkout flow in an explicit transaction, fail atomically on any persistence error, and centralize workflow orchestration in a service layer.  
MVC Target: Service  
Validation: checkout smoke test passed, and a forced failure after dropping `payments` confirmed the transaction rolls back without leaving created users or enrollments behind.  

### [FIXED] [HIGH] Administrative Financial Report Is Unauthenticated And Implements N+1 Query Patterns
File: `ecommerce-api-legacy/src/AppManager.js:80-129`, `ecommerce-api-legacy/api.http:27-28`  
Category: Security | Performance  
Description: The administrative report endpoint is publicly exposed with no authentication or authorization checks. It also queries enrollments per course, then user and payment records per enrollment, creating repeated database round trips inside nested loops.  
Impact: Any caller can access revenue and student information, and response latency will degrade as course and enrollment counts grow.  
Recommendation: Protect the route with admin authentication/authorization and replace the nested query pattern with joined or batched queries handled in a reporting repository/service.  
MVC Target: Controller  
Validation: `GET /api/admin/financial-report` now returns `401` without `x-admin-token`, returns `200` with the configured token, and the repository builds the same report shape from a single joined query path.  

### [FIXED] [HIGH] User Deletion Breaks Referential Integrity And Leaves Dirty Financial Data
File: `ecommerce-api-legacy/src/AppManager.js:131-136`, `ecommerce-api-legacy/src/AppManager.js:14-16`  
Category: Reliability | Architecture  
Description: `DELETE /api/users/:id` removes a user record but intentionally leaves related enrollments and payments behind, as confirmed by the response message. The schema also lacks foreign key constraints to prevent this corruption.  
Impact: The system creates orphaned records, invalid reporting data, and a database state that no longer reflects business reality.  
Recommendation: Enforce referential integrity with foreign keys, define a consistent deletion policy, and move destructive user operations into a dedicated service/repository flow with validation.  
MVC Target: Model  
Validation: deleting `/api/users/1` now removes dependent enrollments and payments, and direct database checks confirmed no orphaned rows remain after the transaction.  

### [FIXED] [MEDIUM] Request Validation Is Incomplete And Uses Obscure Payload Contracts
File: `ecommerce-api-legacy/src/AppManager.js:29-35`, `ecommerce-api-legacy/api.http:7-12`  
Category: Reliability | Maintainability  
Description: The checkout handler reads abbreviated fields such as `usr`, `eml`, `pwd`, `c_id`, and `card`, but only validates `usr`, `eml`, `c_id`, and `card`. It accepts any email shape, any card string, and allows password omission for new users.  
Impact: Invalid or ambiguous input reaches the persistence layer, weakens the API contract, and increases coupling between clients and undocumented internal field names.  
Recommendation: Introduce explicit request validation with clear field names or a compatibility mapping layer, validate formats consistently, and reject incomplete checkout requests before business logic runs.  
MVC Target: Controller  
Validation: checkout now accepts both legacy and explicit field names, and invalid payloads return structured `400` responses with validation details.  

### [FIXED] [MEDIUM] Error Handling Is Inconsistent And Frequently Discards Diagnostic Context
File: `ecommerce-api-legacy/src/AppManager.js:35-38`, `ecommerce-api-legacy/src/AppManager.js:40-41`, `ecommerce-api-legacy/src/AppManager.js:50-61`, `ecommerce-api-legacy/src/AppManager.js:83-127`, `ecommerce-api-legacy/src/AppManager.js:133-135`  
Category: Reliability  
Description: The API returns plain-text ad hoc messages, mixes Portuguese strings with HTTP responses, ignores some callback errors entirely, and in `DELETE /api/users/:id` sends success regardless of `err`. There is no centralized error middleware or response standard.  
Impact: Operational failures can be hidden from clients and maintainers, while API behavior becomes difficult to test and evolve consistently.  
Recommendation: Introduce centralized error handling middleware, standardize response payloads, and ensure every database callback either handles or propagates errors explicitly.  
MVC Target: Middleware  
Validation: centralized error middleware now returns JSON errors for invalid checkout payloads and invalid user IDs, while boot smoke tests still pass.  

### [FIXED] [MEDIUM] Hidden Global Mutable State In Utility Module Creates Uncontrolled Side Effects
File: `ecommerce-api-legacy/src/utils.js:9-15`, `ecommerce-api-legacy/src/AppManager.js:57-60`  
Category: Architecture | Maintainability  
Description: `globalCache` is a module-level mutable object modified by `logAndCache`, and checkout writes into it as a side effect of successful enrollment. `totalRevenue` is also exported globally but never used.  
Impact: Hidden shared state complicates reasoning, testing, and future concurrency behavior while adding dead or misleading infrastructure.  
Recommendation: Remove unused globals, inject explicit collaborators where needed, and isolate caching behind a dedicated service with a clear lifecycle.  
MVC Target: Service  
Validation: checkout still succeeds and the in-memory cache is now observable through the app-owned cache service instead of module-level globals.  

### [FIXED] [LOW] Composition Root Is Minimal And Keeps Boot Logic Tightly Coupled To Concrete Implementation
File: `ecommerce-api-legacy/src/app.js:1-13`  
Category: Architecture  
Description: `app.js` directly instantiates `AppManager`, initializes the database, registers routes, and starts the server with no app factory, dependency wiring boundary, or test-friendly composition mechanism.  
Impact: Bootstrapping is hard to customize for tests or alternative environments, and the application remains tightly coupled to one concrete implementation path.  
Recommendation: Introduce an application factory/composition root that wires config, database, repositories, services, routes, and server startup separately.  
MVC Target: Composition Root  
Validation: `node -e "const { spawn } = require('child_process'); ..."` passed and confirmed `src/app.js` still boots after introducing `createApp()`.  

## Deprecated API Detection

No clearly deprecated Express 4.18.2 APIs were identified in the analyzed files. The dominant issues are security, transactional integrity, and lack of architectural separation rather than framework deprecation.

## Proposed Phase 3 Refactoring Plan

1. [FIXED] Extract environment-aware configuration and remove all hardcoded secrets, seeded real credentials, and sensitive logs.
2. [FIXED] Split `AppManager` into composition root, routes/controllers, services, repositories/models, and middleware following MVC boundaries.
3. [FIXED] Replace `badCrypto` with a real password hashing strategy and require explicit validated credentials in checkout.
4. [FIXED] Refactor checkout into a transactional service that atomically creates users, enrollments, payments, and audit logs.
5. [FIXED] Protect administrative endpoints with authentication/authorization and redesign the financial report query to avoid N+1 access patterns.
6. [FIXED] Enforce referential integrity in the schema and redesign destructive user deletion to preserve consistent domain state.
7. [FIXED] Add centralized request validation and standardized error handling for all endpoints.
8. [FIXED] Remove hidden global mutable state from `utils.js` and replace it with explicit collaborators or eliminate it entirely.
9. [FIXED] Introduce an application factory to decouple bootstrapping from runtime server start.

Phase 2 complete. Proceed with MVC refactoring (Phase 3)? [y/n]
