// ─────────────────────────────────────────────
// VOTE — sans rechargement de page
// ─────────────────────────────────────────────

function voter(morceauId) {
  const bouton = document.getElementById("btn-voter");
  const compteur = document.getElementById("compteur-votes");

  if (!bouton) return;

  // Récupérer le token CSRF
  const csrf = document.cookie
    .split(";")
    .find((c) => c.trim().startsWith("csrftoken="))
    ?.split("=")[1];

  if (!csrf) {
    window.location.href = "/connexion/";
    return;
  }

  // Désactiver le bouton pendant la requête
  bouton.disabled = true;
  bouton.textContent = "⏳ Vote en cours...";

  fetch(`/engagement/voter/${morceauId}/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": csrf,
      "Content-Type": "application/json",
    },
  })
    .then((response) => {
      // Si non connecté → rediriger
      if (response.status === 302 || response.redirected) {
        window.location.href = "/connexion/";
        return null;
      }
      return response.json();
    })
    .then((data) => {
      if (!data) return;

      if (data.succes) {
        // Mettre à jour le compteur
        if (compteur) {
          compteur.textContent = data.nb_votes;
        }

        // Mettre à jour le bouton
        bouton.textContent = "✓ Voté !";
        bouton.classList.add("btn-vote-fait");
        bouton.disabled = true;

        // Afficher un message de succès
        afficherMessage("Vote enregistré avec succès ! +5 points", "success");
      } else {
        // Déjà voté
        bouton.textContent = "✓ Déjà voté";
        bouton.disabled = true;
        bouton.classList.add("btn-vote-fait");
        afficherMessage(data.message, "info");
      }
    })
    .catch((error) => {
      console.error("Erreur vote:", error);
      bouton.disabled = false;
      bouton.textContent = "👍 Voter";
      afficherMessage("Une erreur est survenue. Réessayez.", "error");
    });
}

// ── Afficher un message temporaire ──
function afficherMessage(texte, type) {
  // Créer le conteneur de messages s'il n'existe pas
  let container = document.querySelector('.messages-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'messages-container';
    container.style.cssText = `
      position: fixed;
      top: calc(var(--navbar-height) + 1rem);
      right: 1rem;
      z-index: 3000;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
      max-width: 380px;
    `;
    document.body.appendChild(container);
  }

  const notification = document.createElement('div');
  notification.className = `message message-${type}`;
  notification.innerHTML = `
    ${texte}
    <button class="message-close" onclick="this.parentElement.remove()">✕</button>
  `;

  // Ajouter au conteneur de messages
  container.appendChild(notification);

  // Auto-suppression après 5 secondes
  setTimeout(() => {
    if (notification.parentElement) {
      notification.remove();
    }
  }, 5000);
}

// ── Fonction utilitaire pour obtenir le token CSRF ──
function getCsrfToken() {
  const csrf = document.cookie
    .split(";")
    .find((c) => c.trim().startsWith("csrftoken="))
    ?.split("=")[1];
  return csrf || '';
}
