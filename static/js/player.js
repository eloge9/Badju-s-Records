// ─────────────────────────────────────────────
// PLAYER GLOBAL — persiste entre les pages
// ─────────────────────────────────────────────

const audio = document.getElementById("audio-global");
const miniPlayer = document.getElementById("mini-player");
const playerBtn = document.getElementById("player-btn");
const playerBar = document.getElementById("player-bar");
const playerTitre = document.getElementById("player-titre");
const playerArtiste = document.getElementById("player-artiste");
const playerPochette = document.getElementById("player-pochette");
const playerCurrent = document.getElementById("player-current");
const playerDuration = document.getElementById("player-duration");

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
function jouerMorceau(data) {
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
}

// ── Charger un morceau dans le player ──
function chargerMorceau(data, autoplay) {
  audio.src = data.fichier;

  playerTitre.textContent = data.titre || "—";
  playerArtiste.textContent = data.artiste || "—";

  if (data.pochette) {
    playerPochette.src = data.pochette;
    playerPochette.style.display = "block";
  } else {
    playerPochette.style.display = "none";
  }

  miniPlayer.classList.remove("hidden");

  if (autoplay) {
    audio.play();
    playerBtn.textContent = "⏸";
  }
}

// ── Play / Pause ──
function playerToggle() {
  if (!audio.src) return;

  if (audio.paused) {
    audio.play();
    playerBtn.textContent = "⏸";
  } else {
    audio.pause();
    playerBtn.textContent = "▶";
  }
}

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
