function createMemoryCacheService() {
    const cache = {};

    return {
        store(key, data) {
            console.log(`[LOG] Updating checkout cache for ${key}`);
            cache[key] = data;
        },
        snapshot() {
            return { ...cache };
        },
    };
}

module.exports = { createMemoryCacheService };
