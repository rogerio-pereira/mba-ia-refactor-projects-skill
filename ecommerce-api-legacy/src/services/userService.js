const { exec, get } = require('../db/connection');
const { deleteUser } = require('../repositories/userRepository');

async function removeUser({ db, userId }) {
    const user = await get(db, 'SELECT id FROM users WHERE id = ?', [userId]);

    if (!user) {
        const error = new Error('Usuário não encontrado');
        error.statusCode = 404;
        throw error;
    }

    await exec(db, 'BEGIN TRANSACTION');

    try {
        await deleteUser(db, userId);
        await exec(db, 'COMMIT');
    } catch (error) {
        await exec(db, 'ROLLBACK');
        throw error;
    }
}

module.exports = { removeUser };
