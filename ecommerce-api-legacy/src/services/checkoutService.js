const { exec } = require('../db/connection');
const { findActiveCourseById } = require('../repositories/courseRepository');
const { findUserIdByEmail, createUser } = require('../repositories/userRepository');
const { createEnrollment } = require('../repositories/enrollmentRepository');
const { createPayment } = require('../repositories/paymentRepository');
const { createAuditLog } = require('../repositories/auditLogRepository');
const { hashPassword } = require('./passwordService');

async function checkout({ db, payload, cacheService }) {
    const course = await findActiveCourseById(db, payload.courseId);

    if (!course) {
        const error = new Error('Curso não encontrado');
        error.statusCode = 404;
        throw error;
    }

    const status = payload.cardNumber.startsWith('4') ? 'PAID' : 'DENIED';

    if (status === 'DENIED') {
        const error = new Error('Pagamento recusado');
        error.statusCode = 400;
        throw error;
    }

    await exec(db, 'BEGIN TRANSACTION');

    try {
        let user = await findUserIdByEmail(db, payload.email);

        if (!user) {
            const createdUser = await createUser(db, payload.userName, payload.email, hashPassword(payload.password));
            user = { id: createdUser.lastID };
        }

        const enrollment = await createEnrollment(db, user.id, payload.courseId);

        await createPayment(db, enrollment.lastID, course.price, status);
        await createAuditLog(db, `Checkout curso ${payload.courseId} por ${user.id}`);
        await exec(db, 'COMMIT');

        cacheService.store(`last_checkout_${user.id}`, course.title);

        return { msg: 'Sucesso', enrollment_id: enrollment.lastID };
    } catch (error) {
        await exec(db, 'ROLLBACK');
        throw error;
    }
}

module.exports = { checkout };
