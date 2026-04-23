function errorHandler(err, req, res, next) {
    if (res.headersSent) {
        return next(err);
    }

    const statusCode = err.statusCode || 500;
    const payload = { error: err.statusCode ? err.message : 'Internal Server Error' };

    if (err.details) {
        payload.details = err.details;
    }

    return res.status(statusCode).json(payload);
}

module.exports = { errorHandler };
