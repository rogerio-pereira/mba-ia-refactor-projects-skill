const { createCheckoutController } = require('../controllers/checkoutController');
const { createAdminController } = require('../controllers/adminController');
const { createUserController } = require('../controllers/userController');
const { adminAuth } = require('../middleware/adminAuth');

function registerRoutes(app, dependencies) {
    const checkoutController = createCheckoutController(dependencies);
    const adminController = createAdminController(dependencies);
    const userController = createUserController(dependencies);

    app.post('/api/checkout', checkoutController);
    app.get('/api/admin/financial-report', adminAuth, adminController.financialReport);
    app.delete('/api/users/:id', userController.remove);
}

module.exports = { registerRoutes };
