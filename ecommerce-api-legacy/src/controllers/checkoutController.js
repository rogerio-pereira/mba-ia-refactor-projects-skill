const { logAndCache } = require('../utils');
const { findActiveCourseById } = require('../repositories/courseRepository');
const { findUserIdByEmail, createUser } = require('../repositories/userRepository');
const { createEnrollment } = require('../repositories/enrollmentRepository');
const { createPayment } = require('../repositories/paymentRepository');
const { createAuditLog } = require('../repositories/auditLogRepository');

function createCheckoutController({ db }) {
    return async function checkout(req, res) {
        const userName = req.body.usr;
        const email = req.body.eml;
        const password = req.body.pwd;
        const courseId = req.body.c_id;
        const cardNumber = req.body.card;

        if (!userName || !email || !courseId || !cardNumber) {
            return res.status(400).send('Bad Request');
        }

        try {
            const course = await findActiveCourseById(db, courseId);

            if (!course) {
                return res.status(404).send('Curso não encontrado');
            }

            let user = await findUserIdByEmail(db, email);

            if (!user) {
                const createdUser = await createUser(db, userName, email, password);
                user = { id: createdUser.lastID };
            }

            console.log(`Processing payment for course ${courseId}`);

            const status = cardNumber.startsWith('4') ? 'PAID' : 'DENIED';

            if (status === 'DENIED') {
                return res.status(400).send('Pagamento recusado');
            }

            const enrollment = await createEnrollment(db, user.id, courseId);

            await createPayment(db, enrollment.lastID, course.price, status);
            await createAuditLog(db, `Checkout curso ${courseId} por ${user.id}`);

            logAndCache(`last_checkout_${user.id}`, course.title);

            return res.status(200).json({ msg: 'Sucesso', enrollment_id: enrollment.lastID });
        } catch (error) {
            return res.status(500).send('Erro DB');
        }
    };
}

module.exports = { createCheckoutController };
