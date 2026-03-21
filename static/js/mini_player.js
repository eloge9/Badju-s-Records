// ─────────────────────────────────────────────
// MINI PLAYER - Badju's Records
// ─────────────────────────────────────────────

class MiniPlayer {
    constructor() {
        this.audio = null;
        this.currentMorceau = null;
        this.isPlaying = false;
        this.currentTime = 0;
        this.duration = 0;
        this.volume = 0.7;
        this.playlist = [];
        this.currentIndex = 0;
        this.progressBar = null;
        this.volumeSlider = null;

        this.init();
    }

    init() {
        // Créer l'élément audio
        this.audio = new Audio();
        this.setupAudioEvents();

        // Récupérer les éléments du DOM
        this.getElements();

        // Restaurer l'état depuis sessionStorage
        this.restoreState();

        // Attacher les événements
        this.attachEvents();

        // Mettre à jour l'interface
        this.updateUI();
    }

    getElements() {
        this.progressBar = document.getElementById('player-progress');
        this.volumeSlider = document.getElementById('player-volume');
        this.playPauseBtn = document.getElementById('btn-play-pause');
        this.prevBtn = document.getElementById('btn-prev');
        this.nextBtn = document.getElementById('btn-next');
        this.titreElement = document.getElementById('player-titre');
        this.artisteElement = document.getElementById('player-artiste');
        this.pochetteElement = document.getElementById('player-pochette');
        this.currentTimeElement = document.getElementById('player-current-time');
        this.totalTimeElement = document.getElementById('player-total-time');
    }

    setupAudioEvents() {
        this.audio.addEventListener('loadedmetadata', () => {
            this.duration = this.audio.duration;
            this.updateTimeDisplay();
            this.saveState();
        });

        this.audio.addEventListener('timeupdate', () => {
            this.currentTime = this.audio.currentTime;
            this.updateProgressBar();
            this.updateTimeDisplay();
        });

        this.audio.addEventListener('ended', () => {
            this.playNext();
        });

        this.audio.addEventListener('play', () => {
            this.isPlaying = true;
            this.updatePlayPauseButton();
            this.saveState();
        });

        this.audio.addEventListener('pause', () => {
            this.isPlaying = false;
            this.updatePlayPauseButton();
            this.saveState();
        });

        this.audio.addEventListener('error', (e) => {
            // Ignorer les erreurs quand src est vide (état initial au chargement)
            if (!this.audio.src || this.audio.src === window.location.href || this.audio.src === '') {
                return;
            }
            // Log silencieux uniquement
            console.warn('MiniPlayer: erreur audio', this.audio.src, e);
        });
    }

    attachEvents() {
        // Play/Pause
        if (this.playPauseBtn) {
            this.playPauseBtn.addEventListener('click', () => this.togglePlayPause());
        }

        // Previous/Next
        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', () => this.playPrevious());
        }
        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', () => this.playNext());
        }

        // Progress bar
        if (this.progressBar) {
            this.progressBar.addEventListener('input', (e) => {
                const time = (e.target.value / 100) * this.duration;
                this.audio.currentTime = time;
            });
        }

        // Volume
        if (this.volumeSlider) {
            this.volumeSlider.addEventListener('input', (e) => {
                this.volume = e.target.value / 100;
                this.audio.volume = this.volume;
                this.saveState();
            });

            // Initialiser le volume
            this.volumeSlider.value = this.volume * 100;
        }

        // Événements clavier
        document.addEventListener('keydown', (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

            switch (e.key) {
                case ' ':
                    e.preventDefault();
                    this.togglePlayPause();
                    break;
                case 'ArrowLeft':
                    this.seek(-10);
                    break;
                case 'ArrowRight':
                    this.seek(10);
                    break;
                case 'ArrowUp':
                    this.adjustVolume(0.1);
                    break;
                case 'ArrowDown':
                    this.adjustVolume(-0.1);
                    break;
            }
        });
    }

    loadMorceau(morceau, playlist = []) {
        if (!morceau) return;

        this.currentMorceau = morceau;
        this.playlist = playlist;
        this.currentIndex = playlist.findIndex(m => m.id === morceau.id);

        // Mettre à jour l'interface
        this.updateMorceauInfo();

        // Charger le fichier audio
        this.audio.src = morceau.fichier_mp3;
        this.audio.load();

        // Sauvegarder l'état
        this.saveState();

        // Afficher le player s'il était caché
        const player = document.querySelector('.mini-player');
        if (player) {
            player.classList.remove('hidden');
        }
    }

    updateMorceauInfo() {
        if (!this.currentMorceau) return;

        if (this.titreElement) {
            this.titreElement.textContent = this.currentMorceau.titre;
        }

        if (this.artisteElement) {
            this.artisteElement.textContent = this.currentMorceau.artiste.nom_artiste ||
                this.currentMorceau.artiste.username;
        }

        if (this.pochetteElement) {
            if (this.currentMorceau.pochette) {
                this.pochetteElement.src = this.currentMorceau.pochette;
            } else {
                this.pochetteElement.src = '/static/img/default-cover.jpg';
            }
        }
    }

    togglePlayPause() {
        if (!this.audio.src) return;

        if (this.isPlaying) {
            this.audio.pause();
        } else {
            this.audio.play();
        }
    }

    playNext() {
        if (this.playlist.length === 0) return;

        this.currentIndex = (this.currentIndex + 1) % this.playlist.length;
        const nextMorceau = this.playlist[this.currentIndex];
        this.loadMorceau(nextMorceau, this.playlist);

        // Auto-play
        setTimeout(() => this.audio.play(), 100);
    }

    playPrevious() {
        if (this.playlist.length === 0) return;

        this.currentIndex = this.currentIndex === 0 ?
            this.playlist.length - 1 : this.currentIndex - 1;
        const prevMorceau = this.playlist[this.currentIndex];
        this.loadMorceau(prevMorceau, this.playlist);

        // Auto-play
        setTimeout(() => this.audio.play(), 100);
    }

    seek(seconds) {
        if (!this.audio.src) return;

        const newTime = Math.max(0, Math.min(this.duration, this.currentTime + seconds));
        this.audio.currentTime = newTime;
    }

    adjustVolume(delta) {
        this.volume = Math.max(0, Math.min(1, this.volume + delta));
        this.audio.volume = this.volume;
        if (this.volumeSlider) {
            this.volumeSlider.value = this.volume * 100;
        }
        this.saveState();
    }

    updateProgressBar() {
        if (!this.progressBar || this.duration === 0) return;

        const progress = (this.currentTime / this.duration) * 100;
        this.progressBar.value = progress;
    }

    updateTimeDisplay() {
        if (this.currentTimeElement) {
            this.currentTimeElement.textContent = this.formatTime(this.currentTime);
        }
        if (this.totalTimeElement) {
            this.totalTimeElement.textContent = this.formatTime(this.duration);
        }
    }

    updatePlayPauseButton() {
        if (!this.playPauseBtn) return;

        const icon = this.playPauseBtn.querySelector('i') || this.playPauseBtn;
        if (this.isPlaying) {
            icon.textContent = '⏸';
            icon.title = 'Pause';
        } else {
            icon.textContent = '▶';
            icon.title = 'Play';
        }
    }

    updateUI() {
        this.updateMorceauInfo();
        this.updatePlayPauseButton();
        this.updateProgressBar();
        this.updateTimeDisplay();

        if (this.volumeSlider) {
            this.volumeSlider.value = this.volume * 100;
        }
    }

    formatTime(seconds) {
        if (!seconds || isNaN(seconds)) return '0:00';

        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }

    saveState() {
        const state = {
            currentMorceau: this.currentMorceau ? {
                id: this.currentMorceau.id,
                titre: this.currentMorceau.titre,
                artiste: this.currentMorceau.artiste.nom_artiste || this.currentMorceau.artiste.username,
                pochette: this.currentMorceau.pochette,
                fichier_mp3: this.currentMorceau.fichier_mp3
            } : null,
            currentTime: this.currentTime,
            volume: this.volume,
            isPlaying: this.isPlaying,
            playlist: this.playlist.map(m => ({
                id: m.id,
                titre: m.titre,
                artiste: m.artiste.nom_artiste || m.artiste.username,
                pochette: m.pochette,
                fichier_mp3: m.fichier_mp3
            })),
            currentIndex: this.currentIndex
        };

        sessionStorage.setItem('miniPlayerState', JSON.stringify(state));
    }

    restoreState() {
        try {
            const savedState = sessionStorage.getItem('miniPlayerState');
            if (!savedState) return;

            const state = JSON.parse(savedState);

            // Restaurer le volume
            this.volume = state.volume || 0.7;
            this.audio.volume = this.volume;

            // Restaurer la playlist et le morceau actuel
            if (state.playlist && state.currentMorceau) {
                this.playlist = state.playlist;
                this.currentIndex = state.currentIndex || 0;

                // Recréer l'objet morceau (simplifié)
                this.currentMorceau = {
                    id: state.currentMorceau.id,
                    titre: state.currentMorceau.titre,
                    artiste: {
                        nom_artiste: state.currentMorceau.artiste
                    },
                    pochette: state.currentMorceau.pochette,
                    fichier_mp3: state.currentMorceau.fichier_mp3
                };

                // Charger le morceau
                this.audio.src = this.currentMorceau.fichier_mp3;
                this.audio.load();

                // Restaurer le temps actuel
                if (state.currentTime) {
                    this.audio.currentTime = state.currentTime;
                }

                // Mettre à jour l'interface
                this.updateUI();

                // Restaurer l'état play/pause
                if (state.isPlaying) {
                    // Ne pas auto-play au chargement de la page
                    this.isPlaying = false;
                    this.updatePlayPauseButton();
                }
            }
        } catch (error) {
            console.error('Erreur lors de la restauration de l\'état du player:', error);
        }
    }

    showNotification(message, type = 'info') {
        // Créer une notification temporaire
        const notification = document.createElement('div');
        notification.className = `player-notification player-notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            bottom: 100px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--bg-card);
            color: var(--text-primary);
            padding: 0.75rem 1.5rem;
            border-radius: var(--radius-md);
            border: 1px solid var(--border);
            box-shadow: var(--shadow);
            z-index: 3000;
            animation: slideUp 0.3s ease;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideDown 0.3s ease';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }

    // Méthodes utilitaires publiques
    play() {
        if (this.audio.src) {
            this.audio.play();
        }
    }

    pause() {
        this.audio.pause();
    }

    stop() {
        this.audio.pause();
        this.audio.currentTime = 0;
        this.isPlaying = false;
        this.updatePlayPauseButton();
    }

    setPlaylist(playlist, startIndex = 0) {
        this.playlist = playlist;
        this.currentIndex = startIndex;
        if (playlist[startIndex]) {
            this.loadMorceau(playlist[startIndex], playlist);
        }
    }

    getCurrentMorceau() {
        return this.currentMorceau;
    }

    isCurrentlyPlaying() {
        return this.isPlaying;
    }
}

// Initialiser le mini-player quand le DOM est chargé
document.addEventListener('DOMContentLoaded', () => {
    window.miniPlayer = new MiniPlayer();
});

// Fonctions globales pour interagir avec le player
window.playMorceau = (morceau, playlist = []) => {
    if (window.miniPlayer) {
        window.miniPlayer.loadMorceau(morceau, playlist);
        window.miniPlayer.play();
    }
};

window.togglePlayer = () => {
    if (window.miniPlayer) {
        window.miniPlayer.togglePlayPause();
    }
};
