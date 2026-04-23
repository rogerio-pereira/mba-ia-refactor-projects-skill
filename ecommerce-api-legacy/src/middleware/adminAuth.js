const { config } = require('../config');

function adminAuth(req, res, next) {
    const token = req.header('x-admin-token');

    if (!token || token !== config.adminApiToken) {
        return res.status(401).json({ error: 'Unauthorized' });
    }

    return next();
}

module.exports = { adminAuth };
