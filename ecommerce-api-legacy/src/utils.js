const globalCache = {};

function logAndCache(key, data) {
    console.log(`[LOG] Updating checkout cache for ${key}`);
    globalCache[key] = data;
}

module.exports = { logAndCache, globalCache };
