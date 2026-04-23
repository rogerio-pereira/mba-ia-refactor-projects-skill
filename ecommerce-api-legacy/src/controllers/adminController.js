const { buildFinancialReport } = require('../repositories/reportRepository');

function createAdminController({ db }) {
    return {
        async financialReport(req, res) {
            try {
                const report = await buildFinancialReport(db);
                return res.json(report);
            } catch (error) {
                return res.status(500).send('Erro DB');
            }
        },
    };
}

module.exports = { createAdminController };
