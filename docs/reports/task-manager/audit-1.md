# Architecture Audit: task-manager-api

## Phase 1: Project Analysis

| Item | Analysis |
| --- | --- |
| Language | Python 3.x; the runtime version is not pinned in the repository |
| Framework | Flask 3.0.0 with Flask-SQLAlchemy 3.1.1 and Flask-CORS 4.0.0 |
| Dependencies | `flask`, `flask-sqlalchemy`, `flask-cors`, `marshmallow`, `requests`, `python-dotenv` |
| Domain | Task management API with users, tasks, categories, login, and reporting endpoints |
| Architecture | The project has partial folder separation (`models/`, `routes/`, `services/`, `utils/`), but most use cases still live inside route modules. Validation, business rules, serialization, and database access are mixed in blueprints, with global app/db state and bootstrap side effects in `app.py`. |
| Source files | 17 files analyzed in `task-manager-api`, totaling 1177 lines; 15 Python source files plus README and requirements |
| Entry point | `task-manager-api/app.py`; documented commands are `python seed.py` and `python app.py` |
| Routes | `GET /health`, `GET /`, task CRUD and search/stats routes in `routes/task_routes.py`, user CRUD and login routes in `routes/user_routes.py`, report and category routes in `routes/report_routes.py` |
| Database | SQLite via `SQLALCHEMY_DATABASE_URI = sqlite:///tasks.db` in `task-manager-api/app.py:11`; ORM models are `Task`, `User`, and `Category` |

## Phase 2: Architecture Audit

Project: `task-manager-api`

Stack: Python, Flask, Flask-SQLAlchemy, SQLite

Analyzed scope: `task-manager-api/app.py`, `task-manager-api/database.py`, `task-manager-api/models/*.py`, `task-manager-api/routes/*.py`, `task-manager-api/services/notification_service.py`, `task-manager-api/utils/helpers.py`, `task-manager-api/seed.py`, `task-manager-api/README.md`, `task-manager-api/requirements.txt`

Approximate lines of code: 1177 total lines, including 1158 lines outside README and requirements

### Summary By Severity

| Severity | Count |
| --- | ---: |
| CRITICAL | 2 |
| HIGH | 3 |
| MEDIUM | 3 |
| LOW | 0 |

## Findings

### [FIXED] [CRITICAL] Hardcoded Secrets And Unsafe Runtime Defaults Are Source-Controlled
File: `task-manager-api/app.py:11-13`, `task-manager-api/app.py:34`, `task-manager-api/services/notification_service.py:7-10`  
Category: Security | Architecture  
Description: The application hardcodes the SQLite path, Flask `SECRET_KEY`, SMTP host/user/password, and starts the server with `debug=True` bound to `0.0.0.0`. These values are committed in source instead of being loaded from environment-aware configuration.  
Impact: Secrets and operational defaults cannot be rotated safely, are exposed to anyone with repository access, and `debug=True` materially increases production risk by exposing interactive debug behavior and sensitive stack traces.  
Recommendation: Introduce a config module backed by `.env` and `.env.example`, move all secrets and runtime flags out of source, disable debug by default, and keep only safe placeholders in version-controlled examples.  
MVC Target: Config  
Fixed by introducing `config.py`, `.env.example`, and `.gitignore` updates so Flask and SMTP settings are loaded from the environment.
Validation: `python3 -m py_compile task-manager-api/app.py task-manager-api/config.py task-manager-api/services/notification_service.py` passed. Import smoke check is currently blocked in this environment because `flask_sqlalchemy` is not installed.

### [CRITICAL] Authentication And User Serialization Expose Sensitive Data And Use Weak Credential Handling
File: `task-manager-api/models/user.py:16-32`, `task-manager-api/routes/user_routes.py:33-40`, `task-manager-api/routes/user_routes.py:85-86`, `task-manager-api/routes/user_routes.py:127-129`, `task-manager-api/routes/user_routes.py:185-210`  
Category: Security | Reliability  
Description: `User.to_dict()` returns the stored password hash, and that method is reused by `GET /users/<id>`, `POST /users`, `PUT /users/<id>`, and `POST /login`, so password hashes are returned to API clients. Passwords are hashed with unsalted MD5 in `set_password()` and `check_password()`, and login returns a predictable fake token (`fake-jwt-token-<id>`) instead of a signed credential.  
Impact: The API leaks credential material in normal responses, stores passwords with an obsolete hash function, and implements authentication that can be trivially forged. This breaks basic security guarantees for any non-demo environment.  
Recommendation: Remove password fields from all serializers, replace MD5 with a standard password hashing function such as `werkzeug.security` or `bcrypt`, and implement real signed authentication tokens or session handling behind a dedicated auth service.  
MVC Target: Service  

### [HIGH] Route Modules Act As Controllers, Services, Repositories, And Serializers At Once
File: `task-manager-api/routes/task_routes.py:11-299`, `task-manager-api/routes/user_routes.py:10-211`, `task-manager-api/routes/report_routes.py:12-223`  
Category: Architecture | Maintainability  
Description: The three blueprint modules concentrate request parsing, validation, ORM queries, business rules, response serialization, statistics calculation, and transaction control in single files. For example, `create_task()` and `update_task()` validate fields, look up foreign keys, parse dates, mutate models, and commit transactions inline, while report endpoints compute aggregates directly inside route handlers.  
Impact: The HTTP layer is tightly coupled to persistence and domain logic, which makes testing, reuse, and safe change difficult. Small behavior changes require editing large route files with many unrelated responsibilities.  
Recommendation: Refactor toward explicit controllers/services and model or repository boundaries. Keep routes limited to HTTP mapping, move business rules and orchestration into services, and centralize serialization logic in model schemas or presenter helpers.  
MVC Target: Controller  

### [HIGH] Repeated ORM Access Inside Loops Creates N+1 Query Patterns In List And Report Endpoints
File: `task-manager-api/routes/task_routes.py:14-59`, `task-manager-api/routes/report_routes.py:53-68`, `task-manager-api/routes/report_routes.py:157-165`  
Category: Performance | Maintainability  
Description: `GET /tasks` loads all tasks and then performs additional `User.query.get()` and `Category.query.get()` calls per task. `GET /reports/summary` loads all users and then queries tasks again for each user, and `GET /categories` counts tasks with a separate query per category.  
Impact: Response time and database round trips grow linearly with result size, which will degrade quickly as the dataset grows and makes report endpoints unnecessarily expensive.  
Recommendation: Replace per-item lookups with eager loading (`joinedload`/relationships), grouped aggregate queries, or batched reporting queries owned by dedicated repository/report services.  
MVC Target: Model  

### [HIGH] Validation And Business Rules Are Duplicated Across Routes While The Shared Helper Layer Is Largely Unused
File: `task-manager-api/routes/task_routes.py:85-145`, `task-manager-api/routes/task_routes.py:156-215`, `task-manager-api/routes/user_routes.py:42-90`, `task-manager-api/routes/user_routes.py:92-132`, `task-manager-api/routes/report_routes.py:167-209`, `task-manager-api/utils/helpers.py:57-116`  
Category: Architecture | Maintainability  
Description: Status validation, priority limits, title length checks, date parsing, email validation, and tag normalization are implemented ad hoc in route handlers instead of being centralized. At the same time, `utils/helpers.py` already defines `process_task_data()`, `parse_date()`, `validate_email()`, and shared constants, but routes continue to duplicate equivalent logic and imports such as `marshmallow` are not used at all.  
Impact: Business rules can drift between endpoints, fixes must be applied in multiple places, and there is no single authoritative validation contract for the API. This increases regression risk and makes the codebase harder to evolve.  
Recommendation: Introduce a single validation layer for request payloads, reuse shared constants/helpers or a schema library consistently, and move field normalization out of route functions into dedicated services or schema classes.  
MVC Target: Service  

### [MEDIUM] Error Handling Is Inconsistent And Frequently Hides Failure Causes
File: `task-manager-api/routes/task_routes.py:13-63`, `task-manager-api/routes/task_routes.py:146-154`, `task-manager-api/routes/task_routes.py:217-238`, `task-manager-api/routes/user_routes.py:80-90`, `task-manager-api/routes/user_routes.py:127-132`, `task-manager-api/routes/user_routes.py:144-151`, `task-manager-api/routes/report_routes.py:182-223`, `task-manager-api/utils/helpers.py:43-50`, `task-manager-api/utils/helpers.py:81-89`  
Category: Reliability | Maintainability  
Description: Many endpoints use broad `except:` or generic `except Exception` blocks, often returning a generic message without structured logging or preserving the failure context. Error responses vary by route, and helper functions swallow parsing/type errors and return `None`, forcing callers to infer what happened.  
Impact: Production failures become hard to diagnose, clients receive inconsistent response contracts, and bugs can be silently masked until they surface as corrupted state or incorrect behavior.  
Recommendation: Introduce centralized error handling, replace bare `except:` blocks with narrow exceptions, standardize JSON error payloads, and log enough context for operational debugging without leaking secrets.  
MVC Target: Middleware  

### [MEDIUM] The Codebase Relies On Legacy `Query.get()` Calls Instead Of SQLAlchemy 2 Style Session Access
File: `task-manager-api/routes/task_routes.py:42`, `task-manager-api/routes/task_routes.py:51`, `task-manager-api/routes/task_routes.py:67`, `task-manager-api/routes/task_routes.py:117`, `task-manager-api/routes/task_routes.py:122`, `task-manager-api/routes/task_routes.py:158`, `task-manager-api/routes/task_routes.py:188`, `task-manager-api/routes/task_routes.py:195`, `task-manager-api/routes/task_routes.py:227`, `task-manager-api/routes/user_routes.py:29`, `task-manager-api/routes/user_routes.py:94`, `task-manager-api/routes/user_routes.py:136`, `task-manager-api/routes/user_routes.py:155`, `task-manager-api/routes/report_routes.py:105`, `task-manager-api/routes/report_routes.py:192`, `task-manager-api/routes/report_routes.py:213`  
Category: Maintainability | Reliability  
Description: Route handlers repeatedly call `Model.query.get(...)`, which is a legacy SQLAlchemy query pattern. The project is already on Flask-SQLAlchemy 3.1.1, where `db.session.get(Model, id)` is the modern access path aligned with SQLAlchemy 2.x.  
Impact: Continued use of legacy ORM APIs increases upgrade friction, normalizes outdated patterns across the codebase, and makes future framework migrations riskier than necessary.  
Recommendation: Replace `Model.query.get(...)` with `db.session.get(Model, id)` while refactoring data access into services or repositories so ORM usage is centralized.  
MVC Target: Model  

### [MEDIUM] Application Bootstrap Has Import-Time Side Effects And No Clear Composition Root Boundary
File: `task-manager-api/app.py:9-34`, `task-manager-api/seed.py:2-14`  
Category: Architecture | Reliability  
Description: `app.py` creates the Flask app, configures extensions, registers blueprints, creates tables inside `with app.app_context(): db.create_all()`, and starts the server from the same module. `seed.py` imports `app` and `db` from that module, so merely importing the application performs database bootstrapping side effects.  
Impact: Startup behavior is hard to control in tests and scripts, infrastructure concerns are mixed with runtime entrypoint logic, and alternative configurations cannot be injected cleanly.  
Recommendation: Introduce an application factory or composition root that wires config, extensions, routes, and database initialization explicitly, leaving server startup and seed execution as separate entrypoints.  
MVC Target: Composition Root  

## Deprecated API Detection

The dominant framework-level deprecation issue in the analyzed scope is repeated use of legacy `Query.get()` access in route modules instead of `db.session.get(...)`. No other clearly deprecated Flask 3.0 APIs were identified in the inspected files.

## Proposed Phase 3 Refactoring Plan

1. [FIXED] Extract an environment-aware config module and remove hardcoded Flask and SMTP secrets, debug defaults, and database settings from source files.
2. Replace the current authentication flow with safe password hashing, password-free serializers, and signed auth token generation behind a dedicated auth service.
3. Split each route module into thinner HTTP adapters plus controller/service layers for tasks, users, reports, and categories.
4. Centralize validation and normalization for task, user, and category payloads using shared schemas or a consistent helper/service layer.
5. Refactor list and report queries to avoid N+1 access patterns by using eager loading or aggregate SQL queries.
6. Introduce centralized error handling and structured logging instead of broad bare exceptions.
7. Replace legacy `Query.get()` usage with `db.session.get(...)` and move ORM access behind clearer boundaries.
8. Create an application factory/composition root so app creation, DB initialization, seeding, and server startup are decoupled.

Phase 2 complete. Proceed with MVC refactoring (Phase 3)? [y/n]
