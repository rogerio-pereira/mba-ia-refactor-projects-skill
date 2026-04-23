const { createApp } = require('./createApp');

const { app, config } = createApp();

app.listen(config.port, () => {
    console.log(`Frankenstein LMS rodando na porta ${config.port}...`);
});
