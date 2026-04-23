const { get } = require('../db/connection');

async function findActiveCourseById(db, id) {
    return get(db, 'SELECT * FROM courses WHERE id = ? AND active = 1', [id]);
}

module.exports = { findActiveCourseById };
