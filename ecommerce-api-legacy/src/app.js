const { createApp } = require('./createApp');

(async () => {
    const { app, config } = await createApp();

    app.listen(config.port, () => {
        console.log(`Frankenstein LMS rodando na porta ${config.port}...`);
    });
})();
