const { run } = require('../db/connection');

async function createAuditLog(db, action) {
    return run(db, "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))", [action]);
}

module.exports = { createAuditLog };
