/**
 * SkyMusic Dashboard V6 - Main Application
 * Lightweight, modular, feature-rich
 */

const APP = (() => {
    const POLL_INTERVAL = 3000; // Update every 3 seconds
    let updateInterval = null;
    let autoplayStatus = false;
    let currentLoopMode = 0;
    let currentShuffleStatus = false;
    let updateCount = 0;
    let lastUpdateTime = 0;

    /**
     * Initialize the application
     */
    async function init() {
        console.log('🎵 SkyMusic Dashboard V6 initializing...');
        console.log('📡 API Base URL:', '/api');
        console.log('⏱️ Poll Interval:', POLL_INTERVAL, 'ms');
        
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
        console.log('📊 Live updates enabled - fetching every', POLL_INTERVAL/1000, 'seconds');
    }

    /**
     * Set up all event listeners
     */
    function setupEventListeners() {
        // Playback controls
        if (UI.DOM.pauseBtn) {
            UI.DOM.pauseBtn.addEventListener('click', async () => {
                if (currentState.isPaused) {
                    await API.resume();
                } else {
                    await API.pause();
                }
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
        updateCount++;
        const timeNow = Date.now();
        const timeSinceLastUpdate = timeNow - lastUpdateTime;
        lastUpdateTime = timeNow;
        
        try {
            // Fetch all data in parallel with error handling
            const [nowPlayingData, queueData, botStats] = await Promise.allSettled([
                API.getNowPlaying(),
                API.getQueue(),
                API.getBotStats()
            ]);

            // Log update (every 10 updates to reduce spam)
            if (updateCount % 10 === 0) {
                console.log(`🔄 Update #${updateCount} (Δt: ${timeSinceLastUpdate}ms)`);
            }

            // Update now playing
            if (nowPlayingData.status === 'fulfilled' && nowPlayingData.value) {
                const data = nowPlayingData.value;
                currentState.isPlaying = data.is_playing;
                currentState.isPaused = data.is_paused;
                currentState.position = data.position || 0;
                currentState.song = data.song;

                UI.updateNowPlaying(data);
                UI.updateControls(data);

                // Check if favorited
                if (data.song) {
                    const isFav = Storage.favorites.has(data.song);
                    UI.updateLikeStatus(data.song, isFav);
                    
                    // Add to history if playing
                    if (data.is_playing) {
                        Storage.history.add(data.song);
                    }
                }

                // Connection status
                const connected = data.is_playing || !!data.song;
                if (connected !== currentState.connected) {
                    currentState.connected = connected;
                    UI.setStatus(connected);
                    console.log('🔗 Connection status changed to:', connected ? 'CONNECTED' : 'DISCONNECTED');
                }
            } else if (nowPlayingData.status === 'rejected') {
                console.warn('❌ Failed to fetch now playing:', nowPlayingData.reason);
                UI.setStatus(false);
            }

            // Update queue
            if (queueData.status === 'fulfilled' && queueData.value) {
                const data = queueData.value;
                currentState.queue = data.queue || [];
                UI.updateQueue(data);
                if (updateCount % 10 === 0) {
                    console.log('📋 Queue updated:', data.queue.length, 'songs');
                }
            } else if (queueData.status === 'rejected') {
                console.warn('❌ Failed to fetch queue:', queueData.reason);
            }

            // Update stats
            if (botStats.status === 'fulfilled' && botStats.value) {
                UI.updateBotStats(botStats.value);
            } else if (botStats.status === 'rejected') {
                console.warn('❌ Failed to fetch bot stats:', botStats.reason);
            }

        } catch (err) {
            console.error('❌ UI update error:', err);
            UI.setStatus(false);
        }
    }

    /**
     * Start polling for updates
     */
    function startPolling() {
        if (updateInterval) clearInterval(updateInterval);
        console.log('▶️  Starting polling with interval:', POLL_INTERVAL, 'ms');
        updateInterval = setInterval(() => {
            updateUI().catch(err => {
                console.error('Polling update error:', err);
            });
        }, POLL_INTERVAL);
        console.log('✅ Polling started. Poll interval ID:', updateInterval);
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
