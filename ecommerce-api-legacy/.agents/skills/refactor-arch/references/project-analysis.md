# Project Analysis Heuristics

## Detection Order

1. Identify manifests and lockfiles before reading source files.
2. Identify entry points and route registration.
3. Identify persistence mechanisms.
4. Map request flow across routes, controllers, services, models/repositories, middleware, and config.
5. Count only relevant source files; exclude dependencies, virtual environments, caches, build output, databases, and generated files.

## Language and Framework Signals

- Python: `requirements.txt`, `pyproject.toml`, `.py` files, `pytest.ini`, `tox.ini`.
- Flask: `Flask(...)`, `Blueprint`, `@app.route`, `@blueprint.route`, `flask_sqlalchemy`, `app.run`.
- Node.js: `package.json`, `package-lock.json`, `.js`, `.mjs`, `.cjs`.
- Express: `express()`, `express.Router()`, `app.get/post/put/delete`, middleware registered with `app.use`.

## Dependency and Runtime Signals

- Prefer package scripts and documented README commands.
- For Python, inspect `requirements.txt`, virtual environment hints, `FLASK_APP`, and app factory functions.
- For Node.js, inspect `package.json` scripts, main entry, and environment variables.
- Detect test commands from `pytest`, `unittest`, `jest`, `mocha`, `npm test`, or project-specific scripts.

## Persistence Signals

- Raw SQL: `sqlite3`, `cursor.execute`, string-concatenated queries, template literals in query strings.
- ORM: SQLAlchemy models/sessions, Sequelize, Prisma, TypeORM, Mongoose.
- Database files: `.db`, `.sqlite`, migrations, schema files, seed scripts, repository/model modules.

## Architecture Signals

- Healthy MVC boundaries have route modules with HTTP mapping only, controllers with orchestration, models/repositories with data access, services with domain rules, config modules for environment, middleware for cross-cutting behavior, and a clear composition root.
- Flag files that mix routing, SQL, validation, business rules, serialization, and bootstrapping.
- Flag modules where route handlers directly access persistence or perform multi-step domain workflows.
- Flag global mutable state shared across request handling.

## Domain Inference

Infer domain from route names, table names, model/entity names, seed data, README text, and endpoint paths. Examples: products/orders/users suggest e-commerce; courses/enrollments/payments suggest LMS; tasks/projects/users suggest task management.
