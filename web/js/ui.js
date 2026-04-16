/**
 * UI Module - Modular UI update functions
 * Handles all DOM updates and UI state management
 */

const UI = (() => {
    // DOM Cache
    const DOM = {};

    /**
     * Initialize DOM references (call on page load)
     */
    function initDOM() {
        // Header
        DOM.statusDot = document.getElementById('statusDot');
        DOM.statusText = document.getElementById('statusText');

        // Now Playing
        DOM.albumArt = document.getElementById('albumArt');
        DOM.liveIndicator = document.getElementById('liveIndicator');
        DOM.songTitle = document.getElementById('songTitle');
        DOM.songArtist = document.getElementById('songArtist');
        DOM.requester = document.getElementById('requester');
        DOM.progressBar = document.getElementById('progressBar');
        DOM.progressFill = document.getElementById('progressFill');
        DOM.currentTime = document.getElementById('currentTime');
        DOM.duration = document.getElementById('duration');
        DOM.queueCount = document.getElementById('queueCount');

        // Controls
        DOM.pauseBtn = document.getElementById('pauseBtn');
        DOM.skipBtn = document.getElementById('skipBtn');
        DOM.stopBtn = document.getElementById('stopBtn');

        // New Controls (to be added in HTML)
        DOM.volumeSlider = document.getElementById('volumeSlider');
        DOM.volumeDisplay = document.getElementById('volumeDisplay');
        DOM.loopBtn = document.getElementById('loopBtn');
        DOM.shuffleBtn = document.getElementById('shuffleBtn');
        DOM.likeBtn = document.getElementById('likeBtn');
        DOM.autoplayBtn = document.getElementById('autoplayBtn');

        // Queue
        DOM.queueList = document.getElementById('queueList');
        DOM.queueFooter = document.getElementById('queueFooter');
        DOM.queueTotal = document.getElementById('queueTotal');
        DOM.clearQueueBtn = document.getElementById('clearQueueBtn');

        // Stats (to be added in HTML)
        DOM.botStatsCard = document.getElementById('botStatsCard');
        DOM.uptime = document.getElementById('uptime');
        DOM.totalServers = document.getElementById('totalServers');
        DOM.totalUsers = document.getElementById('totalUsers');
    }

    /**
     * Safely update element text with check
     */
    function setText(element, text) {
        if (element && element.textContent !== String(text)) {
            element.textContent = text;
        }
    }

    /**
     * Format time in MM:SS
     */
    function formatTime(seconds) {
        if (!seconds || seconds < 0) return '0:00';
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    /**
     * Format large numbers (1000 -> 1K)
     */
    function formatNumber(num) {
        if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
        if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
        return num.toString();
    }

    return {
        init: initDOM,
        formatTime,
        formatNumber,

        // Status
        setStatus(connected) {
            if (!DOM.statusDot) return;
            if (connected) {
                DOM.statusDot.classList.add('connected');
                setText(DOM.statusText, 'Connected ✓');
            } else {
                DOM.statusDot.classList.remove('connected');
                setText(DOM.statusText, 'Disconnected');
            }
        },

        // Now Playing
        updateNowPlaying(data) {
            if (!data || !data.song) {
                setText(DOM.songTitle, 'No song playing');
                setText(DOM.songArtist, 'Waiting for /play command...');
                setText(DOM.requester, '-');
                setText(DOM.currentTime, '0:00');
                setText(DOM.duration, '0:00');
                if (DOM.progressFill) DOM.progressFill.style.width = '0%';
                if (DOM.albumArt) DOM.albumArt.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"%3E%3Crect fill="%231e293b" width="200" height="200"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-size="48" fill="%23475569"%3E🎵%3C/text%3E%3C/svg%3E';
                if (DOM.liveIndicator) DOM.liveIndicator.classList.add('hidden');
                return;
            }

            const song = data.song;
            setText(DOM.songTitle, song.title || 'Unknown');
            setText(DOM.songArtist, song.artist || 'Unknown Artist');
            setText(DOM.requester, song.requester || '-');

            // Album art
            if (DOM.albumArt && song.thumbnail) {
                const img = new Image();
                img.onload = () => DOM.albumArt.src = song.thumbnail;
                img.onerror = () => {
                    // Keep current or use placeholder
                };
                img.src = song.thumbnail;
            }

            // Progress
            const duration = song.duration || 0;
            const position = data.position || 0;
            setText(DOM.duration, formatTime(duration));
            setText(DOM.currentTime, formatTime(position));

            if (DOM.progressFill) {
                const percentage = duration > 0 ? (position / duration) * 100 : 0;
                DOM.progressFill.style.width = `${Math.min(percentage, 100)}%`;
            }

            // Live indicator
            if (DOM.liveIndicator) {
                if (data.is_playing) {
                    DOM.liveIndicator.classList.remove('hidden');
                } else {
                    DOM.liveIndicator.classList.add('hidden');
                }
            }
        },

        // Queue
        updateQueue(data) {
            if (!data || !data.queue) {
                if (DOM.queueList) {
                    DOM.queueList.innerHTML = '<div class="queue-empty">Queue is empty. Use /play to add songs!</div>';
                }
                if (DOM.queueFooter) DOM.queueFooter.style.display = 'none';
                return;
            }

            const queue = data.queue;
            const remaining = Math.max(0, queue.length - 1);
            setText(DOM.queueCount, remaining);

            if (queue.length === 0) {
                if (DOM.queueList) {
                    DOM.queueList.innerHTML = '<div class="queue-empty">Queue is empty. Use /play to add songs!</div>';
                }
                if (DOM.queueFooter) DOM.queueFooter.style.display = 'none';
            } else {
                const html = queue
                    .slice(1)
                    .map((item, idx) => {
                        const song = item.song;
                        return `
                            <div class="queue-item" data-index="${item.index}">
                                <div class="queue-item-number">#${idx + 1}</div>
                                <div class="queue-item-info">
                                    <div class="queue-item-title">${this.escapeHtml(song.title)}</div>
                                    <div class="queue-item-artist">${this.escapeHtml(song.artist)}</div>
                                </div>
                                <div class="queue-item-meta">${formatTime(song.duration)}</div>
                                <button class="queue-item-remove" title="Remove" data-index="${item.index}">✕</button>
                            </div>
                        `;
                    })
                    .join('');

                if (DOM.queueList) DOM.queueList.innerHTML = html;
                if (DOM.queueFooter) DOM.queueFooter.style.display = 'block';
                setText(DOM.queueTotal, queue.length);

                // Add event listeners for remove buttons
                if (DOM.queueList) {
                    DOM.queueList.querySelectorAll('.queue-item-remove').forEach(btn => {
                        btn.onclick = (e) => {
                            e.stopPropagation();
                            const idx = parseInt(btn.dataset.index);
                            if (!isNaN(idx)) {
                                APP.removeFromQueue(idx);
                            }
                        };
                    });
                }
            }
        },

        // Controls
        updateControls(data) {
            if (!data) return;

            const playing = data.is_playing && !data.is_paused;

            // Disable buttons when no music
            if (DOM.pauseBtn) DOM.pauseBtn.disabled = !playing && !data.is_paused;
            if (DOM.skipBtn) DOM.skipBtn.disabled = !playing && !data.is_paused;
            if (DOM.stopBtn) DOM.stopBtn.disabled = !playing && !data.is_paused;

            // Update pause button
            if (DOM.pauseBtn) {
                if (data.is_paused) {
                    DOM.pauseBtn.title = 'Resume';
                    DOM.pauseBtn.innerHTML = '<span class="btn-icon">▶️</span>';
                } else {
                    DOM.pauseBtn.title = 'Pause';
                    DOM.pauseBtn.innerHTML = '<span class="btn-icon">⏸️</span>';
                }
            }
        },

        // Volume Control
        updateVolume(volume) {
            if (DOM.volumeSlider) {
                DOM.volumeSlider.value = volume;
            }
            if (DOM.volumeDisplay) {
                setText(DOM.volumeDisplay, `${volume}%`);
            }
        },

        // Loop Mode
        updateLoopMode(mode) {
            if (!DOM.loopBtn) return;
            const modes = ['⤴️', '🔁', '🔀'];
            DOM.loopBtn.innerHTML = `<span class="btn-icon">${modes[mode % 3]}</span>`;
            DOM.loopBtn.title = ['Loop Off', 'Loop One', 'Loop All'][mode % 3];
        },

        // Shuffle Status
        updateShuffleStatus(isShuffled) {
            if (!DOM.shuffleBtn) return;
            if (isShuffled) {
                DOM.shuffleBtn.classList.add('active');
            } else {
                DOM.shuffleBtn.classList.remove('active');
            }
        },

        // Like Button
        updateLikeStatus(song, isFavorite) {
            if (!DOM.likeBtn) return;
            if (isFavorite) {
                DOM.likeBtn.classList.add('liked');
                DOM.likeBtn.innerHTML = '<span class="btn-icon">❤️</span>';
            } else {
                DOM.likeBtn.classList.remove('liked');
                DOM.likeBtn.innerHTML = '<span class="btn-icon">🤍</span>';
            }
        },

        // Autoplay Status
        updateAutoplayStatus(enabled) {
            if (!DOM.autoplayBtn) return;
            if (enabled) {
                DOM.autoplayBtn.classList.add('active');
                DOM.autoplayBtn.title = 'Autoplay: ON';
            } else {
                DOM.autoplayBtn.classList.remove('active');
                DOM.autoplayBtn.title = 'Autoplay: OFF';
            }
        },

        // Stats
        updateBotStats(stats) {
            if (!stats) return;
            if (DOM.uptime) setText(DOM.uptime, stats.uptime || '-');
            if (DOM.totalServers) setText(DOM.totalServers, formatNumber(stats.total_servers || 0));
            if (DOM.totalUsers) setText(DOM.totalUsers, formatNumber(stats.total_users || 0));
        },

        // Utility
        escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        },

        toggleClass(element, className) {
            if (element) element.classList.toggle(className);
        },

        addClass(element, className) {
            if (element) element.classList.add(className);
        },

        removeClass(element, className) {
            if (element) element.classList.remove(className);
        }
    };
})();
