# MVC Architecture Guidelines

## Target Responsibilities

- **Models/Repositories**: persistence objects, query helpers, database abstractions, and domain entity mapping.
- **Views/Routes**: HTTP route declarations, request extraction, response formatting, status codes, and serialization boundaries. For APIs, routes are the view layer.
- **Controllers**: application flow, use-case orchestration, coordination between services/models, and HTTP-independent decisions.
- **Services**: domain rules that do not belong to persistence or HTTP.
- **Config**: environment-based settings, secrets loading, runtime flags, database URLs, and constants.
- **Middleware**: cross-cutting concerns such as error handling, auth checks, CORS, logging, and request context.
- **Composition Root**: application creation, dependency wiring, middleware registration, route registration, and boot command.

## Boundary Rules

- Routes must stay thin and avoid direct SQL or multi-step business workflows.
- Controllers may coordinate multiple services/repositories but should not know raw SQL details.
- Models/repositories should not import route modules or HTTP request objects.
- Services should not construct framework responses.
- Config must not contain real secrets committed to source control.
- Middleware should handle shared behavior once instead of duplicating it in routes.
- The composition root wires dependencies and starts the app; it should not contain business rules.

## Framework Adaptation

- Flask: prefer an app factory when useful, register blueprints as routes/views, use config modules, and keep SQLAlchemy/session usage behind models/repositories for complex operations.
- Express: keep `app.js` or `server.js` as composition root, use routers for HTTP mapping, controllers for request orchestration, services for domain logic, repositories for persistence, and error middleware for exceptions.
- If the project already has partial MVC structure, improve the existing structure instead of creating needless folders.
