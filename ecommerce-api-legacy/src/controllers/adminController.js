const { buildFinancialReport } = require('../repositories/reportRepository');

function createAdminController({ db }) {
    return {
        async financialReport(req, res) {
            const report = await buildFinancialReport(db);
            return res.json(report);
        },
    };
}

module.exports = { createAdminController };
