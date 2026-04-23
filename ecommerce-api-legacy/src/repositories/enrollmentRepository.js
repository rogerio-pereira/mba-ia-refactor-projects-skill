const { all, run } = require('../db/connection');

async function createEnrollment(db, userId, courseId) {
    return run(db, 'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)', [userId, courseId]);
}

async function findEnrollmentsByCourseId(db, courseId) {
    return all(db, 'SELECT * FROM enrollments WHERE course_id = ?', [courseId]);
}

module.exports = { createEnrollment, findEnrollmentsByCourseId };
