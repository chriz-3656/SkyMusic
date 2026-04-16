/**
 * Storage Module - LocalStorage wrapper for favorites, history, and preferences
 * Handles all client-side persistence with expiration
 */

const Storage = (() => {
    const PREFIX = 'skymusic_';
    const HISTORY_MAX = 50; // Keep last 50 songs
    const HISTORY_EXPIRY = 30 * 24 * 60 * 60 * 1000; // 30 days

    /**
     * Get a stored value with namespace
     */
    function get(key, defaultValue = null) {
        try {
            const item = localStorage.getItem(`${PREFIX}${key}`);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.error(`Storage read error [${key}]:`, e);
            return defaultValue;
        }
    }

    /**
     * Set a stored value with namespace
     */
    function set(key, value) {
        try {
            localStorage.setItem(`${PREFIX}${key}`, JSON.stringify(value));
            return true;
        } catch (e) {
            console.error(`Storage write error [${key}]:`, e);
            return false;
        }
    }

    /**
     * Remove a stored value
     */
    function remove(key) {
        try {
            localStorage.removeItem(`${PREFIX}${key}`);
            return true;
        } catch (e) {
            console.error(`Storage remove error [${key}]:`, e);
            return false;
        }
    }

    /**
     * Clear all SkyMusic data
     */
    function clear() {
        try {
            const keys = Object.keys(localStorage)
                .filter(k => k.startsWith(PREFIX));
            keys.forEach(k => localStorage.removeItem(k));
            return true;
        } catch (e) {
            console.error('Storage clear error:', e);
            return false;
        }
    }

    return {
        // Favorites Management
        favorites: {
            get() {
                return get('favorites', []);
            },

            add(song) {
                const favorites = this.get();
                if (!favorites.find(s => s.title === song.title && s.artist === song.artist)) {
                    favorites.push({
                        ...song,
                        favoritedAt: Date.now()
                    });
                    set('favorites', favorites);
                    return true;
                }
                return false;
            },

            remove(song) {
                const favorites = this.get();
                const filtered = favorites.filter(
                    s => !(s.title === song.title && s.artist === song.artist)
                );
                set('favorites', filtered);
                return filtered.length < favorites.length;
            },

            has(song) {
                const favorites = this.get();
                return favorites.some(s => s.title === song.title && s.artist === song.artist);
            },

            clear() {
                remove('favorites');
            }
        },

        // Playback History
        history: {
            get() {
                const history = get('history', []);
                // Remove expired entries
                return history.filter(h => {
                    const age = Date.now() - (h.addedAt || 0);
                    return age < HISTORY_EXPIRY;
                });
            },

            add(song) {
                const history = this.get();
                
                // Remove duplicate if exists
                const filtered = history.filter(
                    s => !(s.title === song.title && s.artist === song.artist)
                );

                // Add to front
                filtered.unshift({
                    ...song,
                    playedAt: Date.now(),
                    addedAt: Date.now()
                });

                // Keep only last N
                const trimmed = filtered.slice(0, HISTORY_MAX);
                set('history', trimmed);
                return trimmed;
            },

            getRecent(count = 10) {
                return this.get().slice(0, count);
            },

            getMostPlayed(count = 10) {
                const history = this.get();
                const grouped = {};
                
                history.forEach(song => {
                    const key = `${song.title}|${song.artist}`;
                    if (!grouped[key]) {
                        grouped[key] = { song, count: 0 };
                    }
                    grouped[key].count++;
                });

                return Object.values(grouped)
                    .map(item => ({ ...item.song, playCount: item.count }))
                    .sort((a, b) => b.playCount - a.playCount)
                    .slice(0, count);
            },

            clear() {
                remove('history');
            }
        },

        // User Preferences
        preferences: {
            get(key, defaultValue = null) {
                const prefs = get('preferences', {});
                return prefs.hasOwnProperty(key) ? prefs[key] : defaultValue;
            },

            set(key, value) {
                const prefs = get('preferences', {});
                prefs[key] = value;
                return set('preferences', prefs);
            },

            getAll() {
                return get('preferences', {});
            },

            setAll(prefs) {
                return set('preferences', prefs);
            },

            clear() {
                remove('preferences');
            }
        },

        // Recent Searches
        searches: {
            get(count = 5) {
                const searches = get('searches', []);
                return searches.slice(0, count);
            },

            add(query) {
                if (!query || query.length < 2) return;
                
                const searches = get('searches', []);
                const filtered = searches.filter(s => s !== query);
                filtered.unshift(query);
                set('searches', filtered.slice(0, 20));
            },

            clear() {
                remove('searches');
            }
        },

        // Last Used Settings
        lastSettings: {
            get() {
                return get('lastSettings', {
                    volume: 100,
                    loopMode: 0,
                    shuffle: false,
                    autoplay: false
                });
            },

            update(settings) {
                const current = this.get();
                const updated = { ...current, ...settings };
                set('lastSettings', updated);
                return updated;
            },

            clear() {
                remove('lastSettings');
            }
        },

        // Cache Management
        clearAll() {
            clear();
        },

        // Debug: Get all stored data
        debug() {
            const data = {};
            Object.keys(localStorage)
                .filter(k => k.startsWith(PREFIX))
                .forEach(k => {
                    data[k.replace(PREFIX, '')] = JSON.parse(localStorage.getItem(k));
                });
            return data;
        }
    };
})();
