const { exec, run } = require('./connection');
const { hashPassword } = require('../services/passwordService');

async function initDb(db) {
    await exec(
        db,
        [
            'PRAGMA foreign_keys = ON',
            'CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, pass TEXT NOT NULL)',
            'CREATE TABLE courses (id INTEGER PRIMARY KEY, title TEXT NOT NULL, price REAL NOT NULL, active INTEGER NOT NULL)',
            'CREATE TABLE enrollments (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, course_id INTEGER NOT NULL, FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE, FOREIGN KEY (course_id) REFERENCES courses(id))',
            'CREATE TABLE payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER NOT NULL, amount REAL NOT NULL, status TEXT NOT NULL, FOREIGN KEY (enrollment_id) REFERENCES enrollments(id) ON DELETE CASCADE)',
            'CREATE TABLE audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)',
        ].join(';'),
    );

    await run(db, 'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)', [
        'Leonan',
        'leonan@fullcycle.com.br',
        hashPassword('seed-password-123'),
    ]);
    await exec(db, "INSERT INTO courses (title, price, active) VALUES ('Clean Architecture', 997.00, 1), ('Docker', 497.00, 1)");
    await run(db, 'INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)');
    await run(db, "INSERT INTO payments (enrollment_id, amount, status) VALUES (1, 997.00, 'PAID')");
}

module.exports = { initDb };
