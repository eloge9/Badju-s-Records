// ─────────────────────────────────────────────
// PLAYER SIMPLE - Badju's Records
// ─────────────────────────────────────────────

// Variables globales
let audio = null;
let miniPlayer = null;
let playerBtn = null;
let playerTitre = null;
let playerArtiste = null;
let playerPochette = null;
let playlist = [];
let indexCourant = 0;

// Initialisation au chargement du DOM
document.addEventListener('DOMContentLoaded', function () {
    console.log("Player: Initialisation...");

    // Récupérer les éléments
    audio = document.getElementById("audio-global");
    miniPlayer = document.getElementById("mini-player");
    playerBtn = document.getElementById("btn-play-pause");
    playerTitre = document.getElementById("player-titre");
    playerArtiste = document.getElementById("player-artiste");
    playerPochette = document.getElementById("player-pochette");

    console.log("Player: Éléments trouvés:", {
        audio: !!audio,
        miniPlayer: !!miniPlayer,
        playerBtn: !!playerBtn,
        playerTitre: !!playerTitre,
        playerArtiste: !!playerArtiste,
        playerPochette: !!playerPochette
    });

    if (!audio) {
        console.error("Player: Élément audio non trouvé!");
        return;
    }

    // Configurer les événements
    audio.addEventListener('timeupdate', updateProgress);
    audio.addEventListener('ended', nextTrack);
    audio.addEventListener('error', function (e) {
        // Ignorer les erreurs quand src est vide (état initial au chargement)
        if (!audio.src || audio.src === window.location.href || audio.src === '') {
            return;
        }
        // Log silencieux uniquement
        console.warn('Player: erreur audio', audio.src, e);
    });

    // Bouton play/pause
    if (playerBtn) {
        playerBtn.addEventListener('click', togglePlay);
    }

    console.log("Player: Initialisation terminée");
});

// ── Fonction principale pour jouer un morceau ──
window.jouerMorceau = function (data) {
    console.log("Player: Jouer morceau:", data);

    // Ajouter à la playlist si pas déjà présent
    const existe = playlist.findIndex(m => m.id === data.id);
    if (existe === -1) {
        playlist.push(data);
        indexCourant = playlist.length - 1;
    } else {
        indexCourant = existe;
    }

    // Charger et jouer
    loadTrack(data, true);
};

// ── Charger un morceau ──
function loadTrack(data, autoplay) {
    console.log("Player: Charger morceau:", data.fichier);

    // Mettre à jour les informations
    if (playerTitre) playerTitre.textContent = data.titre || "—";
    if (playerArtiste) playerArtiste.textContent = data.artiste || "—";

    // Gérer la pochette
    if (playerPochette && data.pochette) {
        playerPochette.src = data.pochette;
        playerPochette.style.display = "block";
    } else if (playerPochette) {
        playerPochette.style.display = "none";
    }

    // Charger le fichier audio proprement
    audio.pause();
    audio.src = '';        // vider d'abord
    audio.src = data.fichier;
    audio.load();          // forcer le rechargement

    // Afficher le mini player
    if (miniPlayer) {
        miniPlayer.classList.remove("hidden");
    }

    // Jouer automatiquement
    if (autoplay) {
        audio.play().catch(function (err) {
            console.log('Autoplay bloqué:', err.message);
        });
    }
}

// ── Play/Pause ──
function togglePlay() {
    if (!audio.src) {
        console.log("Player: Pas de fichier audio chargé");
        return;
    }

    if (audio.paused) {
        audio.play().then(() => {
            if (playerBtn) playerBtn.textContent = "⏸";
        });
    } else {
        audio.pause();
        if (playerBtn) playerBtn.textContent = "▶";
    }
}

// ── Mettre à jour la barre de progression ──
function updateProgress() {
    const current = audio.currentTime;
    const duration = audio.duration || 0;

    // Mettre à jour le temps actuel (si l'élément existe)
    const currentTimeEl = document.getElementById("player-current-time");
    const totalTimeEl = document.getElementById("player-total-time");
    const progressBar = document.getElementById("player-progress");

    if (currentTimeEl) {
        currentTimeEl.textContent = formatTime(current);
    }

    if (totalTimeEl) {
        totalTimeEl.textContent = formatTime(duration);
    }

    if (progressBar && duration > 0) {
        progressBar.value = (current / duration) * 100;
    }
}

// ── Piste suivante ──
function nextTrack() {
    if (playlist.length > 0 && indexCourant < playlist.length - 1) {
        indexCourant++;
        loadTrack(playlist[indexCourant], true);
    }
}

// ── Formatage du temps ──
function formatTime(seconds) {
    if (isNaN(seconds)) return "0:00";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

// ── Fonctions globales pour les boutons ──
window.playerNext = function () {
    nextTrack();
};

window.playerPrev = function () {
    if (playlist.length > 0 && indexCourant > 0) {
        indexCourant--;
        loadTrack(playlist[indexCourant], true);
    }
};

window.playerToggle = togglePlay;
