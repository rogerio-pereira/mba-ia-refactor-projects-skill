# Refactoring Playbook

Apply the smallest safe transformation that addresses the finding while preserving public behavior.

## 1. Extract Hardcoded Config

Before:

```python
app.config["SECRET_KEY"] = "secret"
```

After:

```python
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
```

## 2. Parameterize SQL

Before:

```python
cursor.execute("select * from users where email = '" + email + "'")
```

After:

```python
cursor.execute("select * from users where email = ?", (email,))
```

## 3. Move SQL From Route to Repository

Before:

```javascript
app.get('/orders/:id', async (req, res) => {
  const row = await db.get(`select * from orders where id = ${req.params.id}`)
  res.json(row)
})
```

After:

```javascript
router.get('/orders/:id', orderController.show)
// controller calls orderRepository.findById(req.params.id)
```

## 4. Extract Business Workflow to Service

Before:

```javascript
router.post('/checkout', async (req, res) => {
  // validate cart, calculate totals, create order, update inventory
})
```

After:

```javascript
router.post('/checkout', checkoutController.create)
// controller calls checkoutService.checkout(payload)
```

## 5. Split God Class by Responsibility

Before:

```javascript
class AppManager {
  start() {}
  createUser() {}
  checkout() {}
  report() {}
}
```

After:

```javascript
createApp({ userController, checkoutController, reportController })
```

## 6. Centralize Validation

Before:

```python
if not data.get("email"):
    return {"error": "email required"}, 400
```

After:

```python
payload = validate_create_user(request.get_json())
```

## 7. Centralize Error Handling

Before:

```javascript
try {
  await service.run()
} catch (error) {
  res.status(500).json({ error: error.message })
}
```

After:

```javascript
router.post('/items', controller.create)
app.use(errorHandler)
```

## 8. Replace Deprecated APIs

Before:

```python
user = User.query.get(user_id)
```

After:

```python
user = db.session.get(User, user_id)
```

## 9. Remove Sensitive Fields From Serialization

Before:

```python
return jsonify(user.__dict__)
```

After:

```python
return jsonify(serialize_user(user))
```

## 10. Batch Repeated I/O

Before:

```python
for task in tasks:
    task.user = User.query.get(task.user_id)
```

After:

```python
users = user_repository.find_by_ids({task.user_id for task in tasks})
```

## Validation Examples

- Python syntax/import: `python -m compileall .`
- Flask boot check: import the app or run an app factory in a short process.
- Python tests: `pytest` when present.
- Node syntax: `node --check src/app.js` for relevant files.
- Node tests: `npm test` when present.
- Endpoint smoke checks: start the app briefly and call unchanged routes with `curl` or existing HTTP files.
