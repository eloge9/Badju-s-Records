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

// ─────────────────────────────────────────────
// BARRE DE PROGRESSION — avec support du drag
// ─────────────────────────────────────────────

var enTrainDeSeeker = false;

document.addEventListener('DOMContentLoaded', function () {

    var audio = document.getElementById('audio-global');
    var playerBar = document.getElementById('player-bar');

    if (!audio || !playerBar) return;

    // ── Détecter quand l'utilisateur commence à déplacer la barre ──
    playerBar.addEventListener('mousedown', function () { enTrainDeSeeker = true; });
    playerBar.addEventListener('touchstart', function () { enTrainDeSeeker = true; });

    // ── Quand l'utilisateur relâche → appliquer le seek ──
    playerBar.addEventListener('mouseup', function () {
        if (!audio.duration) return;
        audio.currentTime = (parseFloat(playerBar.value) / 100) * audio.duration;
        enTrainDeSeeker = false;
    });

    playerBar.addEventListener('touchend', function () {
        if (!audio.duration) return;
        audio.currentTime = (parseFloat(playerBar.value) / 100) * audio.duration;
        enTrainDeSeeker = false;
    });

    // ── Sur changement de valeur (clavier, clic direct) ──
    playerBar.addEventListener('change', function () {
        if (!audio.duration) return;
        audio.currentTime = (parseFloat(playerBar.value) / 100) * audio.duration;
    });

    // ── Mettre à jour la barre pendant la lecture ──
    audio.addEventListener('timeupdate', function () {
        if (enTrainDeSeeker) return; // ← ne pas écraser pendant le drag
        if (!audio.duration) return;
        var pct = (audio.currentTime / audio.duration) * 100;
        playerBar.value = pct;

        // Mettre à jour le temps affiché
        var playerCurrent = document.getElementById('player-current-time');
        var playerDuration = document.getElementById('player-total-time');
        if (playerCurrent) playerCurrent.textContent = formaterTemps(audio.currentTime);
        if (playerDuration) playerDuration.textContent = formaterTemps(audio.duration);
    });

});

// ─────────────────────────────────────────────
// SEEK — appelé depuis le template si oninput
// ─────────────────────────────────────────────

function playerSeek(valeur) {
    var audio = document.getElementById('audio-global');
    if (!audio || !audio.duration) return;
    audio.currentTime = (parseFloat(valeur) / 100) * audio.duration;
}

// ─────────────────────────────────────────────
// CONTROLE VOLUME
// ─────────────────────────────────────────────

function playerVolume(valeur) {
    var audio = document.getElementById('audio-global');
    if (!audio) return;
    audio.volume = parseFloat(valeur) / 100;
}

// ─────────────────────────────────────────────
// RESTE DU PLAYER (inchangé)
// ─────────────────────────────────────────────

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

// ── Piste suivante ──
function nextTrack() {
    if (playlist.length > 0 && indexCourant < playlist.length - 1) {
        indexCourant++;
        loadTrack(playlist[indexCourant], true);
    }
}

// ── Formatage du temps ──
function formaterTemps(seconds) {
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

window.playerPlayPause = togglePlay;
