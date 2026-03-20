// ─────────────────────────────────────────────
// PLAYER GLOBAL — persiste entre les pages
// ─────────────────────────────────────────────

// Attendre que le DOM soit chargé
document.addEventListener('DOMContentLoaded', function () {
  // Récupérer les éléments du DOM
  const audio = document.getElementById("audio-global");
  const miniPlayer = document.getElementById("mini-player");
  const playerBtn = document.getElementById("btn-play-pause");
  const playerBar = document.getElementById("player-progress");
  const playerTitre = document.getElementById("player-titre");
  const playerArtiste = document.getElementById("player-artiste");
  const playerPochette = document.getElementById("player-pochette");
  const playerCurrent = document.getElementById("player-current-time");
  const playerDuration = document.getElementById("player-total-time");

  // Vérifier que les éléments existent
  if (!audio || !miniPlayer) {
    console.log("Player: éléments manquants dans le DOM");
    return;
  }

  // File de lecture
  let playlist = [];
  let indexCourant = 0;

  // ── Restaurer l'état depuis sessionStorage ──
  function restaurerPlayer() {
    const etat = sessionStorage.getItem("badjus_player");
    if (!etat) return;

    try {
      const data = JSON.parse(etat);
      playlist = data.playlist || [];
      indexCourant = data.indexCourant || 0;

      if (playlist.length > 0) {
        chargerMorceau(playlist[indexCourant], false);
        miniPlayer.classList.remove("hidden");
      }
    } catch (e) {
      console.log("Player: impossible de restaurer l'état");
    }
  }

  // ── Sauvegarder l'état dans sessionStorage ──
  function sauvegarderPlayer() {
    sessionStorage.setItem(
      "badjus_player",
      JSON.stringify({
        playlist: playlist,
        indexCourant: indexCourant,
      }),
    );
  }

  // ── Jouer un morceau (appelé depuis les pages) ──
  window.jouerMorceau = function (data) {
    // Vérifier si le morceau est déjà dans la playlist
    const existe = playlist.findIndex((m) => m.id === data.id);

    if (existe !== -1) {
      indexCourant = existe;
    } else {
      playlist.push(data);
      indexCourant = playlist.length - 1;
    }

    chargerMorceau(data, true);
    sauvegarderPlayer();
  };

  // ── Charger un morceau dans le player ──
  function chargerMorceau(data, autoplay) {
    audio.src = data.fichier;

    if (playerTitre) playerTitre.textContent = data.titre || "—";
    if (playerArtiste) playerArtiste.textContent = data.artiste || "—";

    if (playerPochette && data.pochette) {
      playerPochette.src = data.pochette;
      playerPochette.style.display = "block";
    } else if (playerPochette) {
      playerPochette.style.display = "none";
    }

    miniPlayer.classList.remove("hidden");

    if (autoplay) {
      audio.play();
      if (playerBtn) playerBtn.textContent = "⏸";
    }
  }

  // ── Play / Pause ──
  function playerToggle() {
    if (!audio.src) return;

    if (audio.paused) {
      audio.play();
      if (playerBtn) playerBtn.textContent = "⏸";
    } else {
      audio.pause();
      if (playerBtn) playerBtn.textContent = "▶";
    }
  }

  // ── Événements audio ──
  audio.addEventListener('timeupdate', function () {
    if (playerCurrent && playerDuration && playerBar) {
      const current = audio.currentTime;
      const duration = audio.duration || 0;

      playerCurrent.textContent = formatTime(current);
      playerDuration.textContent = formatTime(duration);
      playerBar.value = duration ? (current / duration) * 100 : 0;
    }
  });

  audio.addEventListener('ended', function () {
    // Passer au morceau suivant
    if (indexCourant < playlist.length - 1) {
      indexCourant++;
      chargerMorceau(playlist[indexCourant], true);
      sauvegarderPlayer();
    }
  });

  // ── Formatage du temps ──
  function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  }

  // ── Initialisation ──
  if (playerBtn) {
    playerBtn.addEventListener('click', playerToggle);
  }

  if (playerBar) {
    playerBar.addEventListener('input', function () {
      const time = (audio.duration || 0) * (this.value / 100);
      audio.currentTime = time;
    });
  }

  // Restaurer l'état au chargement
  restaurerPlayer();

  // Rendre les fonctions accessibles globalement
  window.playerNext = function () {
    if (playlist.length === 0) return;
    indexCourant = (indexCourant + 1) % playlist.length;
    chargerMorceau(playlist[indexCourant], true);
    sauvegarderPlayer();
  };

  window.playerPrev = function () {
    if (playlist.length === 0) return;
    indexCourant = (indexCourant - 1 + playlist.length) % playlist.length;
    chargerMorceau(playlist[indexCourant], true);
    sauvegarderPlayer();
  };

  window.playerToggle = playerToggle;
});

// ── Morceau suivant ──
function playerNext() {
  if (playlist.length === 0) return;
  indexCourant = (indexCourant + 1) % playlist.length;
  chargerMorceau(playlist[indexCourant], true);
  sauvegarderPlayer();
}

// ── Morceau précédent ──
function playerPrev() {
  if (playlist.length === 0) return;
  indexCourant = (indexCourant - 1 + playlist.length) % playlist.length;
  chargerMorceau(playlist[indexCourant], true);
  sauvegarderPlayer();
}

// ── Déplacer dans le morceau ──
function playerSeek(valeur) {
  if (!audio.duration) return;
  audio.currentTime = (valeur / 100) * audio.duration;
}

// ── Volume ──
function playerVolume(valeur) {
  audio.volume = valeur / 100;
}

// ── Formater le temps en mm:ss ──
function formaterTemps(secondes) {
  if (isNaN(secondes)) return "0:00";
  const m = Math.floor(secondes / 60);
  const s = Math.floor(secondes % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

// ── Mise à jour de la barre de progression ──
audio.addEventListener("timeupdate", () => {
  if (!audio.duration) return;
  const progression = (audio.currentTime / audio.duration) * 100;
  playerBar.value = progression;
  playerCurrent.textContent = formaterTemps(audio.currentTime);
  playerDuration.textContent = formaterTemps(audio.duration);
});

// ── Morceau suivant automatiquement ──
audio.addEventListener("ended", () => {
  playerBtn.textContent = "▶";
  playerNext();
});

// ── Durée chargée ──
audio.addEventListener("loadedmetadata", () => {
  playerDuration.textContent = formaterTemps(audio.duration);
});

// ── Erreur audio ──
audio.addEventListener("error", () => {
  console.log("Player: erreur de chargement audio");
  playerBtn.textContent = "▶";
});

// ── Restaurer au chargement de la page ──
document.addEventListener("DOMContentLoaded", restaurerPlayer);
