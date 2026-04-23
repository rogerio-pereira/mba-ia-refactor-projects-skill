const crypto = require('crypto');

function hashPassword(password) {
    const salt = crypto.randomBytes(16).toString('hex');
    const hashed = crypto.scryptSync(password, salt, 64).toString('hex');
    return `${salt}:${hashed}`;
}

module.exports = { hashPassword };
