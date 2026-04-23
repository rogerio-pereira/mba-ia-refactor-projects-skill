const { logAndCache } = require('../utils');
const { checkout: runCheckout } = require('../services/checkoutService');

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

        if (!password) {
            return res.status(400).send('Password is required');
        }

        console.log(`Processing payment for course ${courseId}`);

        try {
            const result = await runCheckout({
                db,
                payload: {
                    userName,
                    email,
                    password,
                    courseId,
                    cardNumber,
                },
                cacheService: {
                    store: logAndCache,
                },
            });

            return res.status(200).json(result);
        } catch (error) {
            return res.status(error.statusCode || 500).send(error.statusCode ? error.message : 'Erro DB');
        }
    };
}

module.exports = { createCheckoutController };
