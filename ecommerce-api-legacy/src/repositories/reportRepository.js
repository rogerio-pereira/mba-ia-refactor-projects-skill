const { all } = require('../db/connection');

async function buildFinancialReport(db) {
    const rows = await all(
        db,
        `
        SELECT
            courses.id AS course_id,
            courses.title AS course_title,
            users.name AS user_name,
            payments.amount AS payment_amount,
            payments.status AS payment_status
        FROM courses
        LEFT JOIN enrollments ON enrollments.course_id = courses.id
        LEFT JOIN users ON users.id = enrollments.user_id
        LEFT JOIN payments ON payments.enrollment_id = enrollments.id
        ORDER BY courses.id, enrollments.id
        `,
    );

    const reportMap = new Map();

    for (const row of rows) {
        if (!reportMap.has(row.course_id)) {
            reportMap.set(row.course_id, {
                course: row.course_title,
                revenue: 0,
                students: [],
            });
        }

        const courseData = reportMap.get(row.course_id);

        if (row.payment_status === 'PAID') {
            courseData.revenue += row.payment_amount;
        }

        if (row.user_name || row.payment_amount !== null) {
            courseData.students.push({
                student: row.user_name || 'Unknown',
                paid: row.payment_amount || 0,
            });
        }
    }

    return Array.from(reportMap.values());
}

module.exports = { buildFinancialReport };
