const { get, run } = require('../db/connection');

async function findUserIdByEmail(db, email) {
    return get(db, 'SELECT id FROM users WHERE email = ?', [email]);
}

async function createUser(db, name, email, password) {
    return run(db, 'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [name, email, password]);
}

async function deleteUser(db, id) {
    return run(db, 'DELETE FROM users WHERE id = ?', [id]);
}

module.exports = { findUserIdByEmail, createUser, deleteUser };
