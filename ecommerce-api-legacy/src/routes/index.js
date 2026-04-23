const { createCheckoutController } = require('../controllers/checkoutController');
const { createAdminController } = require('../controllers/adminController');
const { createUserController } = require('../controllers/userController');
const { asyncHandler } = require('../middleware/asyncHandler');
const { adminAuth } = require('../middleware/adminAuth');

function registerRoutes(app, dependencies) {
    const checkoutController = createCheckoutController(dependencies);
    const adminController = createAdminController(dependencies);
    const userController = createUserController(dependencies);

    app.post('/api/checkout', asyncHandler(checkoutController));
    app.get('/api/admin/financial-report', adminAuth, asyncHandler(adminController.financialReport));
    app.delete('/api/users/:id', asyncHandler(userController.remove));
}

module.exports = { registerRoutes };
