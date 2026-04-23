# Architecture Audit: code-smells-project

## Phase 1: Project Analysis

| Item | Analysis |
| --- | --- |
| Language | Python, version not pinned in repository |
| Framework | Flask 3.1.1 with flask-cors 5.0.1 |
| Dependencies | `flask`, `flask-cors`, `sqlite3` from the Python standard library |
| Domain | E-commerce API for products, users, orders, login, reports, and health checks |
| Architecture | Partial MVC naming exists, but responsibilities are mixed. Routes and admin handlers live in the app entry point, controllers contain validation, orchestration, notification side effects, and direct database checks, while models mix repositories, serialization, business rules, stock mutation, reporting, and raw SQL. |
| Source files | 6 files analyzed, approximately 794 total lines; 4 Python source files and 2 project metadata/docs files |
| Entry point | `code-smells-project/app.py`; README start command is `python app.py` |
| Routes | `/`, `/produtos`, `/produtos/busca`, `/produtos/<id>`, `/usuarios`, `/usuarios/<id>`, `/login`, `/pedidos`, `/pedidos/usuario/<usuario_id>`, `/pedidos/<pedido_id>/status`, `/relatorios/vendas`, `/health`, `/admin/reset-db`, `/admin/query` |
| Database | SQLite via `code-smells-project/database.py`, global connection to hardcoded `loja.db`, schema and seed data created during first connection |

## Phase 2: Architecture Audit

Project: `code-smells-project`

Stack: Python, Flask, SQLite

Analyzed scope: `app.py`, `controllers.py`, `models.py`, `database.py`, `README.md`, `requirements.txt`

Approximate lines of code: 794 total lines, including 780 Python lines.

### Summary By Severity

| Severity | Count |
| --- | ---: |
| CRITICAL | 5 |
| HIGH | 5 |
| MEDIUM | 5 |
| LOW | 2 |

## Findings

### [CRITICAL] Hardcoded Secret, Debug Mode, And Public Runtime Flags

- **File:** `code-smells-project/app.py:6-9`
- **Category:** Security
- **Description:** The Flask app sets `SECRET_KEY` directly in source code and enables `DEBUG` at import time. CORS is also enabled globally without origin restrictions.
- **Impact:** A committed secret can be reused by attackers, debug mode can expose internals in unsafe deployments, and unrestricted CORS broadens the browser attack surface.
- **Recommendation:** Move secrets, debug flags, and CORS origins into an environment-aware config module. Fail fast when required secrets are missing outside development.
- **MVC Target:** Config

### [CRITICAL] Unauthenticated Arbitrary SQL Execution Endpoint

- **File:** `code-smells-project/app.py:59-78`
- **Category:** Security
- **Description:** `/admin/query` reads a request-provided `sql` string and executes it directly through SQLite. The route has no authentication, authorization, query allowlist, or read-only enforcement.
- **Impact:** Any caller can read, mutate, or delete application data and can bypass every domain rule in controllers and models.
- **Recommendation:** Remove this endpoint from runtime code. If administrative diagnostics are required, implement authenticated admin tooling with explicit operations instead of arbitrary SQL.
- **MVC Target:** Controller

### [CRITICAL] Unauthenticated Destructive Database Reset Endpoint

- **File:** `code-smells-project/app.py:47-57`
- **Category:** Security
- **Description:** `/admin/reset-db` deletes rows from all core tables and is registered without authentication or environment restrictions.
- **Impact:** Any caller can erase products, users, orders, and order items. This is a total data-loss path in any reachable environment.
- **Recommendation:** Remove the endpoint or guard it behind environment checks, strong admin authentication, authorization, CSRF protection where applicable, and audit logging.
- **MVC Target:** Controller

### [CRITICAL] SQL Injection Through String-Concatenated Queries

- **File:** `code-smells-project/models.py:47-60`
- **Category:** Security
- **Description:** Product creation and update build SQL statements by concatenating user-controlled values such as `nome`, `descricao`, and `categoria`.
- **Impact:** Crafted input can alter SQL syntax, corrupt data, bypass intended writes, or cause application errors. The pattern is repeated across several data operations.
- **Recommendation:** Use parameterized SQLite queries for all SQL execution and keep query construction inside repository/model functions.
- **MVC Target:** Model

### [CRITICAL] Plaintext Password Storage And Credential Querying

- **File:** `code-smells-project/models.py:105-129`
- **Category:** Security
- **Description:** User passwords are inserted and compared as plaintext. Login uses direct string interpolation for email and password.
- **Impact:** A database leak exposes all user credentials, password reuse becomes dangerous, and the login query is injectable.
- **Recommendation:** Hash passwords with a current password-hashing function, compare hashes using a safe verification API, and parameterize the login query.
- **MVC Target:** Model

### [HIGH] Sensitive Data Returned By User Queries And Health Endpoint

- **File:** `code-smells-project/models.py:72-103`
- **Category:** Security
- **Description:** User serialization includes the `senha` field in list and detail responses.
- **Impact:** API callers can receive password values. In the current implementation these are plaintext, which turns normal read endpoints into credential disclosure paths.
- **Recommendation:** Create explicit response serializers that exclude secrets and private fields. Ensure user model/repository methods never return password material except to authentication internals.
- **MVC Target:** Model

### [HIGH] Health Endpoint Leaks Configuration And Secret Values

- **File:** `code-smells-project/controllers.py:264-290`
- **Category:** Security
- **Description:** `/health` returns `db_path`, `debug`, and `secret_key` values in the HTTP response.
- **Impact:** A low-friction diagnostic endpoint discloses deployment details and the application secret to any caller.
- **Recommendation:** Restrict health output to non-sensitive status fields. Move deeper diagnostics to authenticated operational tooling.
- **MVC Target:** Controller

### [HIGH] Global Mutable Database Connection With Cross-Thread SQLite Access

- **File:** `code-smells-project/database.py:4-11`
- **Category:** Reliability
- **Description:** The app stores a module-level `db_connection` and opens SQLite with `check_same_thread=False`.
- **Impact:** A shared mutable connection can create concurrency bugs, hidden transaction coupling, and difficult-to-reproduce failures under concurrent requests.
- **Recommendation:** Use Flask request-scoped database connections through `g`, close them on teardown, and keep database creation/wiring in the composition root.
- **MVC Target:** Composition Root

### [HIGH] God Module Combining Multiple Domains And Responsibilities

- **File:** `code-smells-project/models.py:4-314`
- **Category:** Architecture
- **Description:** One `models.py` module handles products, users, authentication, orders, stock mutation, reports, serialization, and discount rules.
- **Impact:** The module is hard to test and change safely. Domain changes in one area can affect unrelated behavior and make ownership unclear.
- **Recommendation:** Split persistence and domain behavior into cohesive modules, such as product repository/service, user repository/auth service, order service, and reporting service.
- **MVC Target:** Model

### [HIGH] Business Workflow And Side Effects Embedded In Controllers

- **File:** `code-smells-project/controllers.py:188-220`
- **Category:** Architecture
- **Description:** Order creation validates request data, calls model logic, formats responses, and simulates email, SMS, and push notification side effects through `print`.
- **Impact:** HTTP controllers become hard to test and reuse, and notification behavior cannot be replaced, retried, or observed cleanly.
- **Recommendation:** Move order workflow and notification orchestration into services. Keep controllers focused on request parsing, invoking use cases, and producing responses.
- **MVC Target:** Service

### [MEDIUM] N+1 Queries When Loading Orders And Items

- **File:** `code-smells-project/models.py:171-201`
- **Category:** Performance
- **Description:** For each order, the code queries order items, then for each item queries product names.
- **Impact:** Response time and database load grow quickly with the number of orders and items.
- **Recommendation:** Fetch orders, items, and product names with joins or batched queries, then assemble the response in memory.
- **MVC Target:** Model

### [MEDIUM] N+1 Query Pattern Duplicated In All-Orders Listing

- **File:** `code-smells-project/models.py:203-233`
- **Category:** Performance
- **Description:** `get_todos_pedidos` repeats the same per-order and per-item query pattern used by the user-specific order listing.
- **Impact:** The endpoint duplicates a known performance issue and increases maintenance cost because fixes must be applied in multiple places.
- **Recommendation:** Extract a shared order-loading query or repository helper that supports optional filters and uses joins or batched lookups.
- **MVC Target:** Model

### [MEDIUM] Order Creation Performs Repeated Reads And Non-Atomic Stock Updates

- **File:** `code-smells-project/models.py:133-169`
- **Category:** Reliability
- **Description:** Order creation reads each product once for validation and total calculation, then reads product prices again while inserting items and updating stock. There is no explicit transaction boundary or rollback path around the multi-step workflow.
- **Impact:** Concurrent requests can oversell stock or leave inconsistent state if an exception occurs mid-flow.
- **Recommendation:** Wrap order creation in an explicit transaction, fetch product rows once, validate quantities, insert order and items, and update stock with guarded conditions.
- **MVC Target:** Service

### [MEDIUM] Request Parsing And Validation Are Duplicated Across Controllers

- **File:** `code-smells-project/controllers.py:24-62`
- **Category:** Maintainability
- **Description:** Product creation performs field presence, type-adjacent, range, length, and category validation inline in the route handler.
- **Impact:** Validation rules are spread through controllers, are difficult to reuse, and are easy to make inconsistent with update/search behavior.
- **Recommendation:** Extract request validators or schema objects for products and map validation failures to consistent API responses.
- **MVC Target:** Controller

### [MEDIUM] Error Responses Expose Raw Exception Details

- **File:** `code-smells-project/controllers.py:5-292`
- **Category:** Reliability
- **Description:** Most controller functions catch `Exception` and return `str(e)` to clients.
- **Impact:** Internal implementation details, SQL errors, and stack-adjacent messages can leak to callers. The repeated pattern also prevents consistent error handling and observability.
- **Recommendation:** Introduce centralized error handling middleware with safe public messages and structured server-side logging.
- **MVC Target:** Middleware

### [LOW] Database Schema And Seed Data Are Created As A Side Effect Of `get_db`

- **File:** `code-smells-project/database.py:7-84`
- **Category:** Architecture
- **Description:** Opening a database connection also creates tables and inserts sample data when the products table is empty.
- **Impact:** Runtime database access has hidden bootstrapping side effects, making tests and production startup less predictable.
- **Recommendation:** Move schema creation and seeding to explicit migration/seed commands or a clearly named initialization function.
- **MVC Target:** Composition Root

### [LOW] Hardcoded Domain Values And Magic Strings Are Scattered

- **File:** `code-smells-project/controllers.py:52-54`
- **Category:** Maintainability
- **Description:** Product categories are hardcoded inside the product creation controller. Status values are also hardcoded in the status update controller at lines 237-243.
- **Impact:** Domain rules become difficult to audit and can diverge between create, update, search, and reporting behavior.
- **Recommendation:** Centralize category and status constants in domain modules or validation schemas and reuse them across controllers and services.
- **MVC Target:** Helper

## Deprecated API Detection

No deprecated Flask API usage was identified in the inspected files. Route registration through `app.add_url_rule` and `@app.route` is still supported in Flask 3.1.1. The larger issue is architectural placement and security, not framework deprecation.

## Proposed Phase 3 Refactoring Plan

1. Create configuration and composition-root boundaries: load `SECRET_KEY`, debug flag, database path, and CORS origins from environment-aware config; wire the Flask app through an app factory.
2. Remove or hard-disable unsafe admin endpoints; if required for the exercise, replace them with authenticated, explicit admin operations.
3. Replace every concatenated SQL statement with parameterized queries and add repository helpers for products, users, orders, and reports.
4. Introduce request-scoped SQLite connection management with teardown cleanup.
5. Split `models.py` into cohesive persistence/domain modules and move order creation business workflow into an order service.
6. Add password hashing and safe login verification; stop returning password fields from user responses.
7. Centralize validation and error handling through validators plus Flask error handlers/middleware.
8. Rewrite order listing to avoid N+1 queries and share loading logic between all-orders and user-orders endpoints.
9. Move schema creation and seed data into explicit initialization commands or scripts.
10. Validate route compatibility for all documented endpoints and preserve response schemas unless a breaking change is explicitly approved.

Phase 2 complete. Proceed with MVC refactoring (Phase 3)? [y/n]
