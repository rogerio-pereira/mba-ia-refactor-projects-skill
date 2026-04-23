const { logAndCache } = require('../utils');
const { createHttpError } = require('../errors/httpError');
const { checkout: runCheckout } = require('../services/checkoutService');
const { normalizeCheckoutPayload, validateCheckoutPayload } = require('../validation/checkoutValidator');

function createCheckoutController({ db }) {
    return async function checkout(req, res) {
        const payload = normalizeCheckoutPayload(req.body);
        const validationErrors = validateCheckoutPayload(payload);

        if (validationErrors.length > 0) {
            throw createHttpError(400, 'Validation failed', validationErrors);
        }

        console.log(`Processing payment for course ${payload.courseId}`);

        const result = await runCheckout({
            db,
            payload: {
                ...payload,
                courseId: Number(payload.courseId),
            },
            cacheService: {
                store: logAndCache,
            },
        });

        return res.status(200).json(result);
    };
}

module.exports = { createCheckoutController };
