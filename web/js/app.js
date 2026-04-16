/**
 * SkyMusic Dashboard V6 - Main Application
 * Lightweight, modular, feature-rich
 */

const APP = (() => {
    const POLL_INTERVAL = 2000; // Update every 2 seconds
    let updateInterval = null;
    let autoplayStatus = false;
    let currentLoopMode = 0;
    let currentShuffleStatus = false;

    /**
     * Initialize the application
     */
    async function init() {
        console.log('🎵 SkyMusic Dashboard V6 initializing...');
        
        // Initialize modules
        UI.init();

        // Set up event listeners
        setupEventListeners();

        // Load last saved settings
        loadSettings();

        // Initial UI update
        await updateUI();

        // Start polling
        startPolling();

        console.log('✅ SkyMusic Dashboard ready');
    }

    /**
     * Set up all event listeners
     */
    function setupEventListeners() {
        // Playback controls
        if (UI.DOM.pauseBtn) {
            UI.DOM.pauseBtn.addEventListener('click', async () => {
                const endpoint = currentState.isPaused ? API.resume : API.pause;
                await endpoint();
                await updateUI();
            });
        }

        if (UI.DOM.skipBtn) {
            UI.DOM.skipBtn.addEventListener('click', async () => {
                await API.skip();
                await updateUI();
            });
        }

        if (UI.DOM.stopBtn) {
            UI.DOM.stopBtn.addEventListener('click', async () => {
                await API.stop();
                await updateUI();
            });
        }

        // Volume control
        if (UI.DOM.volumeSlider) {
            UI.DOM.volumeSlider.addEventListener('change', async (e) => {
                const volume = parseInt(e.target.value);
                await API.setVolume(volume);
                Storage.preferences.set('volume', volume);
            });
        }

        // Loop toggle
        if (UI.DOM.loopBtn) {
            UI.DOM.loopBtn.addEventListener('click', async () => {
                await API.toggleLoop();
                currentLoopMode = (currentLoopMode + 1) % 3;
                UI.updateLoopMode(currentLoopMode);
                Storage.preferences.set('loopMode', currentLoopMode);
            });
        }

        // Shuffle toggle
        if (UI.DOM.shuffleBtn) {
            UI.DOM.shuffleBtn.addEventListener('click', async () => {
                await API.toggleShuffle();
                currentShuffleStatus = !currentShuffleStatus;
                UI.updateShuffleStatus(currentShuffleStatus);
                Storage.preferences.set('shuffle', currentShuffleStatus);
            });
        }

        // Like button
        if (UI.DOM.likeBtn) {
            UI.DOM.likeBtn.addEventListener('click', async () => {
                if (currentState.song) {
                    const isFav = Storage.favorites.has(currentState.song);
                    if (isFav) {
                        Storage.favorites.remove(currentState.song);
                    } else {
                        Storage.favorites.add(currentState.song);
                    }
                    UI.updateLikeStatus(currentState.song, !isFav);
                }
            });
        }

        // Autoplay toggle
        if (UI.DOM.autoplayBtn) {
            UI.DOM.autoplayBtn.addEventListener('click', async () => {
                await API.toggleAutoplay();
                autoplayStatus = !autoplayStatus;
                UI.updateAutoplayStatus(autoplayStatus);
                Storage.preferences.set('autoplay', autoplayStatus);
            });
        }

        // Clear queue
        if (UI.DOM.clearQueueBtn) {
            UI.DOM.clearQueueBtn.addEventListener('click', async () => {
                if (confirm('Clear entire queue?')) {
                    await API.clearQueue();
                    await updateUI();
                }
            });
        }

        // Progress bar seek
        if (UI.DOM.progressBar) {
            UI.DOM.progressBar.addEventListener('click', (e) => {
                if (!currentState.song) return;
                const rect = UI.DOM.progressBar.getBoundingClientRect();
                const percentage = (e.clientX - rect.left) / rect.width;
                const newPosition = percentage * currentState.song.duration;
                API.seek(newPosition);
            });
        }
    }

    /**
     * Load saved settings from storage
     */
    function loadSettings() {
        const prefs = Storage.preferences.getAll();
        
        if (prefs.volume) {
            UI.updateVolume(prefs.volume);
        }
        if (prefs.loopMode !== undefined) {
            currentLoopMode = prefs.loopMode;
            UI.updateLoopMode(currentLoopMode);
        }
        if (prefs.shuffle) {
            currentShuffleStatus = prefs.shuffle;
            UI.updateShuffleStatus(currentShuffleStatus);
        }
        if (prefs.autoplay) {
            autoplayStatus = prefs.autoplay;
            UI.updateAutoplayStatus(autoplayStatus);
        }
    }

    /**
     * State management
     */
    let currentState = {
        song: null,
        isPlaying: false,
        isPaused: false,
        queue: [],
        position: 0,
        connected: false
    };

    /**
     * Update entire UI
     */
    async function updateUI() {
        try {
            const [nowPlayingData, queueData, botStats] = await Promise.all([
                API.getNowPlaying(),
                API.getQueue(),
                API.getBotStats()
            ]);

            // Update now playing
            if (nowPlayingData) {
                currentState.isPlaying = nowPlayingData.is_playing;
                currentState.isPaused = nowPlayingData.is_paused;
                currentState.position = nowPlayingData.position || 0;
                currentState.song = nowPlayingData.song;

                UI.updateNowPlaying(nowPlayingData);
                UI.updateControls(nowPlayingData);

                // Check if favorited
                if (nowPlayingData.song) {
                    const isFav = Storage.favorites.has(nowPlayingData.song);
                    UI.updateLikeStatus(nowPlayingData.song, isFav);
                    
                    // Add to history if playing
                    if (nowPlayingData.is_playing) {
                        Storage.history.add(nowPlayingData.song);
                    }
                }

                // Connection status
                const connected = nowPlayingData.is_playing || !!nowPlayingData.song;
                if (connected !== currentState.connected) {
                    currentState.connected = connected;
                    UI.setStatus(connected);
                }
            }

            // Update queue
            if (queueData) {
                currentState.queue = queueData.queue || [];
                UI.updateQueue(queueData);
            }

            // Update stats
            if (botStats) {
                UI.updateBotStats(botStats);
            }

        } catch (err) {
            console.error('UI update error:', err);
        }
    }

    /**
     * Start polling for updates
     */
    function startPolling() {
        if (updateInterval) clearInterval(updateInterval);
        updateInterval = setInterval(updateUI, POLL_INTERVAL);
    }

    /**
     * Stop polling
     */
    function stopPolling() {
        if (updateInterval) {
            clearInterval(updateInterval);
            updateInterval = null;
        }
    }

    /**
     * Remove song from queue
     */
    async function removeFromQueue(index) {
        await API.removeFromQueue(index);
        await updateUI();
    }

    /**
     * Public API
     */
    return {
        init,
        removeFromQueue,
        updateUI,
        startPolling,
        stopPolling,
        // Expose state for debugging
        getState: () => currentState,
        getStorage: () => Storage.debug()
    };
})();

/**
 * Initialize on DOM ready
 */
document.addEventListener('DOMContentLoaded', () => {
    APP.init();
});

/**
 * Stop polling when page unloads
 */
window.addEventListener('beforeunload', () => {
    APP.stopPolling();
});
