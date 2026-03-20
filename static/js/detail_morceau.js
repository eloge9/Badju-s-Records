// ─────────────────────────────────────────────
// PAGE DÉTAIL MORCEAU
// ─────────────────────────────────────────────

// ── Initialisation des données du morceau ──
document.addEventListener('DOMContentLoaded', function() {
  // Données injectées depuis le template
  if (typeof window.currentMorceau !== 'undefined') {
    // Le morceau est déjà chargé via window.currentMorceau
    console.log('Morceau chargé:', window.currentMorceau);
  }
  
  if (typeof window.playlistData !== 'undefined') {
    // La playlist est déjà chargée via window.playlistData
    console.log('Playlist chargée:', window.playlistData);
  }
});

// ── Fonctions pour le player ──
function jouerAutreMorceau(morceauId) {
  // Trouver le morceau dans la playlist
  const morceau = window.playlistData.find(m => m.id === morceauId);
  if (morceau && window.miniPlayer) {
    window.miniPlayer.loadMorceau(morceau, window.playlistData);
    window.miniPlayer.play();
  }
}

// ── Vote pour morceau (remplace la fonction existante) ──
function voterPourMorceau(morceauId) {
  const btn = document.getElementById('vote-btn-' + morceauId);
  if (!btn) return;
  
  btn.disabled = true;
  btn.innerHTML = '⏳ Vote en cours...';
  
  fetch(`/engagement/voter/${morceauId}/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-CSRFToken': getCsrfToken()
    },
    body: ''
  })
  .then(response => response.json())
  .then(data => {
    if (data.succes) {
      btn.innerHTML = '✓ Déjà voté';
      btn.disabled = true;

      // Mettre à jour les points affichés
      const pointsElements = document.querySelectorAll('.stat-number');
      if (pointsElements[0]) {
        pointsElements[0].textContent = data.points;
      }

      // Notification
      showNotification('Vote enregistré avec succès !', 'success');
    } else {
      showNotification(data.message || 'Erreur lors du vote', 'error');
      btn.disabled = false;
      btn.innerHTML = '👍 Voter';
    }
  })
  .catch(error => {
    console.error('Erreur:', error);
    showNotification('Une erreur est survenue', 'error');
    btn.disabled = false;
    btn.innerHTML = '👍 Voter';
  });
}

// ── Partage de morceau ──
function partagerMorceau(morceauId) {
  const url = window.location.href;

  if (navigator.share) {
    navigator.share({
      title: document.title,
      url: url
    });
  } else {
    // Copier dans le presse-papiers
    navigator.clipboard.writeText(url).then(() => {
      showNotification('Lien copié dans le presse-papiers !', 'success');
    });
  }
}

// ── Utilitaires ──
function getCsrfToken() {
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    const parts = cookie.trim().split('=');
    if (parts[0] === 'csrftoken') {
      return decodeURIComponent(parts[1]);
    }
  }
  return '';
}

function showNotification(message, type) {
  type = type || 'info';

  // Créer une notification temporaire
  const notification = document.createElement('div');
  notification.className = 'message message-' + type;
  notification.innerHTML = message + '<button class="message-close" onclick="this.parentElement.remove()">✕</button>';

  // Ajouter au conteneur de messages
  let container = document.querySelector('.messages-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'messages-container';
    container.style.cssText = 'position: fixed; top: calc(var(--navbar-height) + 1rem); right: 1rem; z-index: 3000; display: flex; flex-direction: column; gap: 0.75rem; max-width: 380px;';
    document.body.appendChild(container);
  }

  container.appendChild(notification);

  // Auto-suppression après 5 secondes
  setTimeout(() => {
    if (notification.parentElement) {
      notification.remove();
    }
  }, 5000);
}
