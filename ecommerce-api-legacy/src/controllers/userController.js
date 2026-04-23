const { createHttpError } = require('../errors/httpError');
const { removeUser } = require('../services/userService');

function createUserController({ db }) {
    return {
        async remove(req, res) {
            const userId = Number(req.params.id);

            if (!Number.isInteger(userId) || userId <= 0) {
                throw createHttpError(400, 'User id must be a positive integer');
            }

            await removeUser({ db, userId });
            return res.send('Usuário e dados relacionados deletados com sucesso.');
        },
    };
}

module.exports = { createUserController };
