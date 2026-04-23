const express = require('express');
const { config } = require('./config');
const { createDatabase } = require('./db/connection');
const { initDb } = require('./db/initDb');
const { errorHandler } = require('./middleware/errorHandler');
const { createMemoryCacheService } = require('./services/cacheService');
const { registerRoutes } = require('./routes');

async function createApp() {
    const app = express();
    const db = createDatabase();
    const cacheService = createMemoryCacheService();

    await initDb(db);

    app.use(express.json());

    registerRoutes(app, { db, cacheService });
    app.use(errorHandler);

    return { app, config, cacheService };
}

module.exports = { createApp };
