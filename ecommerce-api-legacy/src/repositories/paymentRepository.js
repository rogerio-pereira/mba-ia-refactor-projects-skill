const { get, run } = require('../db/connection');

async function createPayment(db, enrollmentId, amount, status) {
    return run(db, 'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)', [enrollmentId, amount, status]);
}

async function findPaymentByEnrollmentId(db, enrollmentId) {
    return get(db, 'SELECT amount, status FROM payments WHERE enrollment_id = ?', [enrollmentId]);
}

module.exports = { createPayment, findPaymentByEnrollmentId };
