const { all, get } = require('../db/connection');
const { findEnrollmentsByCourseId } = require('./enrollmentRepository');
const { findPaymentByEnrollmentId } = require('./paymentRepository');

async function buildFinancialReport(db) {
    const report = [];
    const courses = await all(db, 'SELECT * FROM courses');

    for (const course of courses) {
        const courseData = { course: course.title, revenue: 0, students: [] };
        const enrollments = await findEnrollmentsByCourseId(db, course.id);

        for (const enrollment of enrollments) {
            const user = await get(db, 'SELECT name, email FROM users WHERE id = ?', [enrollment.user_id]);
            const payment = await findPaymentByEnrollmentId(db, enrollment.id);

            if (payment && payment.status === 'PAID') {
                courseData.revenue += payment.amount;
            }

            courseData.students.push({
                student: user ? user.name : 'Unknown',
                paid: payment ? payment.amount : 0,
            });
        }

        report.push(courseData);
    }

    return report;
}

module.exports = { buildFinancialReport };
