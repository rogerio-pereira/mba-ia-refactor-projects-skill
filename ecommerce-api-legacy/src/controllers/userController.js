const { deleteUser } = require('../repositories/userRepository');

function createUserController({ db }) {
    return {
        async remove(req, res) {
            await deleteUser(db, req.params.id);
            return res.send('Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.');
        },
    };
}

module.exports = { createUserController };
