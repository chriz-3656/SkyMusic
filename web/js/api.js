/**
 * API Module - Wrapper for all backend API calls
 * Handles request caching, error handling, and request deduplication
 */

const API = (() => {
    const BASE_URL = 'http://localhost:8000/api';
    const CACHE_DURATION = 2000; // 2 seconds
    const cache = new Map();

    /**
     * Internal fetch with caching and error handling
     */
    async function fetchAPI(endpoint, options = {}) {
        const cacheKey = `${options.method || 'GET'}:${endpoint}`;
        const now = Date.now();

        // Return cached result if valid
        if (cache.has(cacheKey)) {
            const cached = cache.get(cacheKey);
            if (now - cached.timestamp < CACHE_DURATION) {
                return cached.data;
            }
        }

        try {
            const response = await fetch(`${BASE_URL}${endpoint}`, {
                method: options.method || 'GET',
                headers: {
                    'Cache-Control': 'no-cache',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();

            // Cache successful GET requests
            if (!options.method || options.method === 'GET') {
                cache.set(cacheKey, { data, timestamp: now });
            }

            return data;
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error.message);
            return null;
        }
    }

    /**
     * Invalidate cache for a specific endpoint
     */
    function invalidateCache(endpoint) {
        const keys = Array.from(cache.keys()).filter(k => k.includes(endpoint));
        keys.forEach(k => cache.delete(k));
    }

    return {
        // Player Control
        async getNowPlaying() {
            return fetchAPI('/now-playing');
        },

        async getQueue() {
            return fetchAPI('/queue');
        },

        async pause() {
            invalidateCache('/now-playing');
            return fetchAPI('/pause', { method: 'POST' });
        },

        async resume() {
            invalidateCache('/now-playing');
            return fetchAPI('/resume', { method: 'POST' });
        },

        async skip() {
            invalidateCache('/now-playing');
            invalidateCache('/queue');
            return fetchAPI('/skip', { method: 'POST' });
        },

        async stop() {
            invalidateCache('/now-playing');
            invalidateCache('/queue');
            return fetchAPI('/stop', { method: 'POST' });
        },

        // Volume Control
        async setVolume(volume) {
            invalidateCache('/now-playing');
            return fetchAPI('/volume', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ volume: Math.max(0, Math.min(100, volume)) })
            });
        },

        async getVolume() {
            return fetchAPI('/volume');
        },

        // Loop Control
        async toggleLoop() {
            invalidateCache('/now-playing');
            return fetchAPI('/loop', { method: 'POST' });
        },

        async getLoopMode() {
            return fetchAPI('/loop');
        },

        // Shuffle Control
        async toggleShuffle() {
            invalidateCache('/queue');
            return fetchAPI('/shuffle', { method: 'POST' });
        },

        async getShuffleStatus() {
            return fetchAPI('/shuffle');
        },

        // Queue Management
        async removeFromQueue(index) {
            invalidateCache('/queue');
            return fetchAPI(`/queue/remove/${index}`, { method: 'POST' });
        },

        async clearQueue() {
            invalidateCache('/queue');
            return fetchAPI('/queue/clear', { method: 'POST' });
        },

        async reorderQueue(fromIndex, toIndex) {
            invalidateCache('/queue');
            return fetchAPI('/queue/reorder', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ from: fromIndex, to: toIndex })
            });
        },

        // Autoplay
        async toggleAutoplay(enabled = null) {
            // If enabled is null, toggle the current state
            const currentStatus = await this.getAutoplayStatus();
            const newState = enabled !== null ? enabled : !currentStatus.enabled;
            
            invalidateCache('/autoplay');
            return fetchAPI('/autoplay', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ enabled: newState })
            });
        },

        async getAutoplayStatus() {
            return fetchAPI('/autoplay');
        },

        // Seek
        async seek(position) {
            return fetchAPI('/seek', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ position: Math.max(0, position) })
            });
        },

        // Favorites
        async addFavorite(songId) {
            return fetchAPI('/favorites/add', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ song_id: songId })
            });
        },

        async removeFavorite(songId) {
            return fetchAPI('/favorites/remove', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ song_id: songId })
            });
        },

        async getFavorites() {
            return fetchAPI('/favorites');
        },

        // Statistics
        async getBotStats() {
            return fetchAPI('/bot/stats');
        },

        async getHistory() {
            return fetchAPI('/bot/history');
        },

        async getTopSongs() {
            return fetchAPI('/bot/top');
        },

        async getTodayStats() {
            return fetchAPI('/stats/today');
        },

        async getServerInfo(guildId) {
            return fetchAPI(`/server/${guildId}`);
        },

        // Utility
        invalidateCache,
        clearCache() {
            cache.clear();
        }
    };
})();
