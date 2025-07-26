const cache = new Map();
export const getCached = (key) => cache.get(key);
export const setCached = (key, data) => cache.set(key, data);
