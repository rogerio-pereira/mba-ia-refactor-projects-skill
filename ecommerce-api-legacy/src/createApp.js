const express = require('express');
const { config } = require('./config');
const { createDatabase } = require('./db/connection');
const { initDb } = require('./db/initDb');
const { registerRoutes } = require('./routes');

async function createApp() {
    const app = express();
    const db = createDatabase();

    await initDb(db);

    app.use(express.json());

    registerRoutes(app, { db });

    return { app, config };
}

module.exports = { createApp };
