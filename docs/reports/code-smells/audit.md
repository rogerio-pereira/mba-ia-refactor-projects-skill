# Architecture Audit: code-smells-project

## Phase 1: Project Analysis

| Item | Analysis |
| --- | --- |
| Language | Python, version not pinned in the repository |
| Framework | Flask 3.1.1 with `flask-cors` 5.0.1 |
| Dependencies | `flask`, `flask-cors`, `sqlite3` from the Python standard library |
| Domain | E-commerce API for products, users, login, orders, reports, and operational/admin endpoints |
| Architecture | Partial MVC naming exists, but responsibilities are heavily mixed. `app.py` contains app bootstrap plus unsafe admin routes, `controllers.py` contains validation and workflow logic, `models.py` mixes repositories, business rules, reporting, and serialization, and `database.py` hides schema/bootstrap side effects behind connection access. |
| Source files | 6 files analyzed, 794 total lines; 4 Python source files plus README and dependency manifest |
| Entry point | `code-smells-project/app.py`; documented start command is `python app.py` |
| Routes | `/`, `/produtos`, `/produtos/busca`, `/produtos/<id>`, `/usuarios`, `/usuarios/<id>`, `/login`, `/pedidos`, `/pedidos/usuario/<usuario_id>`, `/pedidos/<pedido_id>/status`, `/relatorios/vendas`, `/health`, `/admin/reset-db`, `/admin/query` |
| Database | SQLite via `code-smells-project/database.py`, global connection to hardcoded `loja.db`, schema creation and seed insertion performed during first `get_db()` call |

## Phase 2: Architecture Audit

Project: `code-smells-project`

Stack: Python, Flask, SQLite

Analyzed scope: `app.py`, `controllers.py`, `models.py`, `database.py`, `README.md`, `requirements.txt`

Approximate lines of code: 794 total lines, including 780 Python lines

### Summary By Severity

| Severity | Count |
| --- | ---: |
| CRITICAL | 5 |
| HIGH | 5 |
| MEDIUM | 5 |
| LOW | 2 |

## Findings

### [FIXED] [CRITICAL] Hardcoded Secret And Unsafe Runtime Defaults
File: `code-smells-project/app.py:6-9`  
Category: Security | Architecture  
Description: The Flask app is instantiated with a hardcoded `SECRET_KEY`, `DEBUG` is forced to `True`, and CORS is enabled globally without origin restrictions.  
Impact: Source-controlled secrets, debug-enabled runtime behavior, and unrestricted browser access materially increase exposure in any non-local deployment.  
Recommendation: Move runtime configuration into an environment-aware config module, require secrets outside development, default debug to disabled, and restrict allowed CORS origins. Create a .env and .env.example files (populate .env with current secrets in codebase).   
MVC Target: Config  
Validation: `python3 -m py_compile app.py config.py controllers.py models.py database.py` passed; `python3` import smoke test for `app` passed.  

### [FIXED] [CRITICAL] Unauthenticated Destructive Database Reset Endpoint
File: `code-smells-project/app.py:47-57`  
Category: Security | Reliability  
Description: `/admin/reset-db` deletes all records from the main tables and is publicly registered with no authentication, authorization, or environment guard.  
Impact: Any caller with network access can erase core business data in a single request.  
Recommendation: Remove the endpoint from runtime code or protect it with strict admin authentication, environment gating, and audit logging.  
MVC Target: Controller  
Validation: `python3 -m py_compile app.py config.py controllers.py models.py database.py` passed; route smoke check confirmed `/admin/reset-db` is absent from `app.url_map`.  

### [FIXED] [CRITICAL] Unauthenticated Arbitrary SQL Execution Endpoint
File: `code-smells-project/app.py:59-78`  
Category: Security  
Description: `/admin/query` executes raw SQL supplied by the request body and commits non-`SELECT` statements directly against the database.  
Impact: This enables complete data exfiltration, modification, or destruction while bypassing every domain rule in the application.  
Recommendation: Remove arbitrary SQL execution from the HTTP surface. If admin diagnostics are required, expose explicit authenticated operations instead.  
MVC Target: Controller  
Validation: `python3 -m py_compile app.py config.py controllers.py models.py database.py` passed; route smoke check confirmed `/admin/query` is absent from `app.url_map`.  

### [FIXED] [CRITICAL] SQL Injection Across Product, User, Order, And Search Queries
File: `code-smells-project/models.py:28-29`, `code-smells-project/models.py:47-60`, `code-smells-project/models.py:68-68`, `code-smells-project/models.py:92-92`, `code-smells-project/models.py:109-110`, `code-smells-project/models.py:126-129`, `code-smells-project/models.py:140-165`, `code-smells-project/models.py:174-174`, `code-smells-project/models.py:188-192`, `code-smells-project/models.py:220-224`, `code-smells-project/models.py:279-280`, `code-smells-project/models.py:289-299`  
Category: Security  
Description: The model layer repeatedly builds SQL with string concatenation using request-derived data such as names, emails, passwords, status, search terms, IDs, and order item values.  
Impact: Malicious input can alter query structure, read unauthorized data, corrupt records, or destroy tables.  
Recommendation: Replace every concatenated statement with parameterized queries and centralize query construction in repository-style functions.  
MVC Target: Model  
Validation: `python3 -m py_compile app.py config.py controllers.py models.py database.py` passed; model smoke test confirmed injected search/login payloads no longer alter query behavior.  

### [CRITICAL] Plaintext Password Storage And Authentication By Raw Query Match
File: `code-smells-project/models.py:79-83`, `code-smells-project/models.py:99-99`, `code-smells-project/models.py:105-120`, `code-smells-project/models.py:122-129`  
Category: Security  
Description: Passwords are inserted, stored, and compared as plaintext. Authentication checks credentials with a raw SQL lookup rather than using password hashing and verification.  
Impact: Any database leak immediately exposes reusable credentials, and login security is far below minimum acceptable practice.  
Recommendation: Hash passwords with a current password hashing algorithm, verify them through a safe API, and never return password data from application reads.  
MVC Target: Model  

### [HIGH] User Read APIs Leak Password Fields
File: `code-smells-project/models.py:72-87`, `code-smells-project/models.py:89-103`  
Category: Security  
Description: User list and detail serializers include the `senha` field in API responses.  
Impact: Standard read endpoints become credential disclosure paths, which is especially severe because passwords are stored in plaintext.  
Recommendation: Introduce explicit safe serializers for user responses and keep password material isolated to authentication internals.  
MVC Target: Model  

### [HIGH] Health Endpoint Leaks Secret And Deployment Details
File: `code-smells-project/controllers.py:264-290`  
Category: Security  
Description: The health handler returns the database path, debug flag, hardcoded environment label, and the application secret key.  
Impact: Operational metadata and secrets are disclosed to any caller through an endpoint that is typically assumed to be low risk.  
Recommendation: Restrict health responses to non-sensitive liveness data and move diagnostics behind authenticated operational tooling.  
MVC Target: Controller  

### [FIXED] [HIGH] Global Mutable SQLite Connection Shared Across Requests
File: `code-smells-project/database.py:4-11`  
Category: Reliability  
Description: The database module stores a single module-level SQLite connection and disables thread checks with `check_same_thread=False`.  
Impact: Shared mutable state creates hidden coupling between requests, makes transaction boundaries unclear, and can surface concurrency bugs under load.  
Recommendation: Use request-scoped connection management, close connections on teardown, and wire database access from the composition root.  
MVC Target: Composition Root  
Validation: `python3 -m py_compile app.py config.py controllers.py models.py database.py` passed; app-context smoke test confirmed per-context connection reuse and teardown wiring.  

### [FIXED] [HIGH] God Model Module Concentrates Multiple Domains And Responsibilities
File: `code-smells-project/models.py:1-314`  
Category: Architecture | Maintainability  
Description: `models.py` contains product persistence, user persistence, authentication, order creation, stock mutation, sales reporting, serialization, and query assembly in one module.  
Impact: The module is difficult to test, risky to modify, and violates clear ownership boundaries between domains and layers.  
Recommendation: Split the module into cohesive repositories/services by domain, separating persistence concerns from business workflow and reporting.  
MVC Target: Model  
Validation: `python3 -m py_compile app.py config.py controllers.py database.py models.py product_repository.py user_repository.py order_repository.py report_repository.py auth_service.py order_service.py` passed; app-context smoke test confirmed the compatibility facade still serves product and order reads.  

### [HIGH] Order Workflow And Notification Side Effects Are Embedded In Controller Code
File: `code-smells-project/controllers.py:188-220`  
Category: Architecture  
Description: The order creation handler performs request validation, invokes model workflow, interprets errors, and triggers email/SMS/push side effects via `print`.  
Impact: HTTP handling, business orchestration, and infrastructure concerns are tightly coupled, making testing and future changes unnecessarily expensive.  
Recommendation: Move order creation and notification orchestration into a dedicated service layer, leaving the controller responsible only for HTTP mapping.  
MVC Target: Service  

### [MEDIUM] N+1 Query Pattern In User Order Listing
File: `code-smells-project/models.py:171-201`  
Category: Performance  
Description: `get_pedidos_usuario` loads orders, then queries items per order, then queries product names per item with extra cursors inside loops.  
Impact: Database round trips scale poorly with the number of orders and items, degrading latency and throughput.  
Recommendation: Fetch orders, items, and product data through joins or batched queries and assemble the response in memory.  
MVC Target: Model  

### [MEDIUM] Same N+1 Logic Is Duplicated In All-Orders Listing
File: `code-smells-project/models.py:203-233`  
Category: Performance | Maintainability  
Description: `get_todos_pedidos` repeats the same per-order and per-item querying strategy used in the user-specific listing.  
Impact: The performance issue is duplicated and any future fix must be applied in multiple places.  
Recommendation: Extract a shared order retrieval routine with optional filters and optimized data loading.  
MVC Target: Model  

### [MEDIUM] Order Creation Lacks Transaction Boundaries And Re-Reads Product State
File: `code-smells-project/models.py:133-169`  
Category: Reliability  
Description: Order creation validates inventory in one loop, then re-queries products in a second loop, inserts rows, and decrements stock without an explicit transaction or rollback strategy.  
Impact: Partial writes or concurrent requests can leave orders and stock in inconsistent states.  
Recommendation: Wrap the workflow in an explicit transaction, fetch product state once, validate atomically, and update stock with guarded writes.  
MVC Target: Service  

### [MEDIUM] Request Validation Is Repeated And Inconsistent Across Controllers
File: `code-smells-project/controllers.py:24-62`, `code-smells-project/controllers.py:64-96`, `code-smells-project/controllers.py:146-165`, `code-smells-project/controllers.py:167-186`, `code-smells-project/controllers.py:188-220`, `code-smells-project/controllers.py:237-255`  
Category: Maintainability  
Description: Validation rules for products, users, login, orders, and status updates are handwritten inline in route handlers, with different shapes and incomplete coverage.  
Impact: Validation logic is hard to reuse, easy to drift, and expensive to test consistently across endpoints.  
Recommendation: Extract validators or schema objects for request payloads and map validation failures to a standard error response format.  
MVC Target: Controller  

### [MEDIUM] Error Handling Repeats Broad `except Exception` Blocks And Returns Raw Errors To Clients
File: `code-smells-project/controllers.py:5-292`, `code-smells-project/app.py:77-78`  
Category: Reliability  
Description: Handlers broadly catch `Exception`, expose `str(e)` in responses, and mix response formatting with console `print` statements.  
Impact: Internal details leak to clients, observability is inconsistent, and the codebase lacks a central policy for translating domain or infrastructure failures into HTTP responses.  
Recommendation: Add centralized error handling with safe public messages and structured server-side logging.  
MVC Target: Middleware  

### [LOW] Database Bootstrap And Seed Data Are Hidden Inside Connection Access
File: `code-smells-project/database.py:7-84`  
Category: Architecture  
Description: `get_db()` not only opens a connection but also creates tables and inserts seed data when the products table is empty.  
Impact: A simple read path triggers schema/bootstrap behavior, which makes startup semantics unclear and complicates testing and production hardening.  
Recommendation: Move schema creation and seeding into explicit initialization commands or a dedicated startup routine.  
MVC Target: Composition Root  

### [LOW] Domain Constants And Environment Labels Are Hardcoded In Multiple Layers
File: `code-smells-project/controllers.py:52-54`, `code-smells-project/controllers.py:242-243`, `code-smells-project/controllers.py:285-289`, `code-smells-project/database.py:5`  
Category: Maintainability  
Description: Product categories, order status values, environment metadata, debug flags, secret labels, and database path literals are embedded directly in handlers and modules.  
Impact: Domain rules and operational settings are difficult to audit, reuse, or change safely.  
Recommendation: Centralize constants and runtime settings in configuration and domain modules, and reuse them across controllers and services.  
MVC Target: Helper  

## Deprecated API Detection

No deprecated Flask API usage was identified in the inspected files. The main issues are security, layering, and data-access design rather than framework deprecation.

## Proposed Phase 3 Refactoring Plan

1. [FIXED] Introduce an environment-aware configuration module and application factory to separate config, bootstrapping, and route registration.
2. [FIXED] Remove or hard-disable `/admin/reset-db` and `/admin/query`, or replace them with explicitly scoped authenticated admin operations if the exercise requires them.
3. [FIXED] Replace all concatenated SQL with parameterized queries and reorganize persistence code into cohesive repository/model modules.
4. [FIXED] Introduce request-scoped SQLite connection handling with deterministic teardown instead of a module-level global connection.
5. [FIXED] Split `models.py` into product, user/auth, order, and reporting modules, and move workflow orchestration into services.
6. Hash passwords, verify them safely during login, and remove password fields from all API serializers.
7. Extract request validation and add centralized error handling for consistent HTTP error responses.
8. Rewrite order retrieval paths to avoid N+1 queries and share the retrieval logic between list variants.
9. Move schema creation and seed loading out of `get_db()` into an explicit initialization path.
10. Re-validate all existing routes to preserve endpoint compatibility while improving separation of responsibilities.

Phase 2 complete. Proceed with MVC refactoring (Phase 3)? [y/n]
