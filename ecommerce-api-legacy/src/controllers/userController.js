const { removeUser } = require('../services/userService');

function createUserController({ db }) {
    return {
        async remove(req, res) {
            try {
                await removeUser({ db, userId: req.params.id });
                return res.send('Usuário e dados relacionados deletados com sucesso.');
            } catch (error) {
                return res.status(error.statusCode || 500).send(error.statusCode ? error.message : 'Erro DB');
            }
        },
    };
}

module.exports = { createUserController };
