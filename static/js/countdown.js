// ─────────────────────────────────────────────
// COUNTDOWN — publicité avant téléchargement
// ─────────────────────────────────────────────

function ouvrirModalTelechargement(morceauId) {
  // Vérifier si connecté via meta tag dans le template
  const estConnecte = document.getElementById("user-connecte");

  if (!estConnecte) {
    window.location.href = "/connexion/";
    return;
  }

  // Récupérer une publicité aléatoire
  fetch("/publicites/aleatoire/")
    .then((response) => response.json())
    .then((pub) => {
      afficherModal(morceauId, pub);
    })
    .catch(() => {
      // Si pas de pub disponible, télécharger directement
      validerTelechargement(morceauId, false);
    });
}

// ── Afficher la modal avec la pub ──
function afficherModal(morceauId, pub) {
  // Supprimer une modal existante
  const ancienne = document.getElementById("modal-pub");
  if (ancienne) ancienne.remove();

  const duree = pub ? pub.duree_secondes : 5;

  const modal = document.createElement("div");
  modal.id = "modal-pub";
  modal.className = "modal-overlay";
  modal.innerHTML = `
    <div class="modal-box">
      <div class="modal-header">
        <span class="modal-titre">Publicité</span>
        <span class="modal-countdown" id="countdown-texte">Attendez ${duree}s</span>
      </div>

      <div class="modal-pub-contenu">
        ${
          pub && pub.image
            ? `<img src="${pub.image}" alt="publicité" class="modal-pub-image">`
            : ""
        }
        ${
          pub && pub.video
            ? `<video autoplay muted class="modal-pub-video">
               <source src="${pub.video}">
             </video>`
            : ""
        }
        ${
          !pub || (!pub.image && !pub.video)
            ? `<div class="modal-pub-vide">
               <p>🎵 Badju's Records</p>
               <p>Votre téléchargement commence dans ${duree}s</p>
             </div>`
            : ""
        }
      </div>

      ${
        pub && pub.url_cible
          ? `<a href="${pub.url_cible}" target="_blank" class="modal-pub-lien">
             En savoir plus →
           </a>`
          : ""
      }

      <button
        id="btn-fermer-modal"
        class="btn btn-gold btn-full"
        onclick="fermerModal(${morceauId})"
        disabled>
        ⏳ Patientez <span id="countdown-btn">${duree}</span>s
      </button>
    </div>
  `;

  document.body.appendChild(modal);

  // Démarrer le countdown
  demarrerCountdown(duree, morceauId);
}

// ── Countdown ──
function demarrerCountdown(duree, morceauId) {
  let restant = duree;
  const btnFermer = document.getElementById("btn-fermer-modal");
  const countdownBtn = document.getElementById("countdown-btn");
  const countdownTexte = document.getElementById("countdown-texte");

  const interval = setInterval(() => {
    restant--;

    if (countdownBtn) countdownBtn.textContent = restant;
    if (countdownTexte) countdownTexte.textContent = `Attendez ${restant}s`;

    if (restant <= 0) {
      clearInterval(interval);

      // Débloquer le bouton
      if (btnFermer) {
        btnFermer.disabled = false;
        btnFermer.textContent = "⬇ Télécharger maintenant";
      }
      if (countdownTexte) {
        countdownTexte.textContent = "✓ Prêt !";
        countdownTexte.style.color = "var(--accent-green)";
      }

      // Valider automatiquement le téléchargement
      validerTelechargement(morceauId, true);
    }
  }, 1000);

  // Stocker l'interval pour pouvoir l'annuler
  modal.dataset.interval = interval;
}

// ── Fermer la modal ──
function fermerModal(morceauId) {
  const modal = document.getElementById("modal-pub");
  if (modal) {
    clearInterval(modal.dataset.interval);
    modal.remove();
  }
}

// ── Valider le téléchargement côté serveur ──
function validerTelechargement(morceauId, pubVue) {
  const csrf = document.cookie
    .split(";")
    .find((c) => c.trim().startsWith("csrftoken="))
    ?.split("=")[1];

  const formData = new FormData();
  formData.append("pub_vue", pubVue ? "true" : "false");

  fetch(`/engagement/telecharger/${morceauId}/`, {
    method: "POST",
    headers: { "X-CSRFToken": csrf },
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.succes) {
        // Déclencher le téléchargement
        const lien = document.createElement("a");
        lien.href = data.url;
        lien.download = "";
        lien.style.display = "none";
        document.body.appendChild(lien);
        lien.click();
        document.body.removeChild(lien);
      }
    })
    .catch((error) => {
      console.error("Erreur téléchargement:", error);
    });
}
