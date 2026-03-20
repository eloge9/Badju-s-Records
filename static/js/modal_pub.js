// ─────────────────────────────────────────────
// MODAL PUBLICITÉ - Badju's Records
// ─────────────────────────────────────────────

class ModalPublicite {
    constructor() {
        this.modal = null;
        this.countdownElement = null;
        this.closeButton = null;
        this.telechargerButton = null;
        this.countdown = 7;
        this.countdownInterval = null;
        this.morceauId = null;
        this.morceauUrl = null;
        
        this.init();
    }

    init() {
        // Créer la modal dans le DOM
        this.createModal();
        
        // Attacher les événements
        this.attachEvents();
    }

    createModal() {
        const modalHTML = `
            <div id="modal-publicite" class="modal-pub">
                <div class="modal-pub-content">
                    <div class="modal-pub-header">
                        <h3>Publicité - Badju's Records</h3>
                    </div>
                    <div class="modal-pub-body">
                        <div class="pub-container">
                            <!-- La publicité sera chargée ici -->
                            <div id="pub-content" class="pub-content">
                                <div class="pub-placeholder">
                                    <p>Chargement de la publicité...</p>
                                </div>
                            </div>
                        </div>
                        <div class="countdown-container">
                            <div class="countdown-timer">
                                <span id="countdown-number">7</span>
                                <span>secondes</span>
                            </div>
                            <p class="countdown-text">Veuillez patienter avant de télécharger</p>
                        </div>
                    </div>
                    <div class="modal-pub-footer">
                        <button id="btn-fermer-modal" class="btn btn-outline" disabled>
                            Fermer (<span id="countdown-close">7</span>s)
                        </button>
                        <button id="btn-telecharger-apres-pub" class="btn btn-gold" disabled>
                            Télécharger
                        </button>
                    </div>
                </div>
                <div class="modal-pub-backdrop"></div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        // Récupérer les éléments
        this.modal = document.getElementById('modal-publicite');
        this.countdownElement = document.getElementById('countdown-number');
        this.closeButton = document.getElementById('btn-fermer-modal');
        this.telechargerButton = document.getElementById('btn-telecharger-apres-pub');
        this.countdownCloseElement = document.getElementById('countdown-close');
    }

    attachEvents() {
        // Bouton fermer
        this.closeButton.addEventListener('click', () => this.fermerModal());
        
        // Bouton télécharger après pub
        this.telechargerButton.addEventListener('click', () => this.telecharger());
        
        // Click sur le backdrop pour fermer (seulement si countdown terminé)
        const backdrop = this.modal.querySelector('.modal-pub-backdrop');
        backdrop.addEventListener('click', () => {
            if (this.countdown <= 0) {
                this.fermerModal();
            }
        });
        
        // Touche Échap pour fermer (seulement si countdown terminé)
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.countdown <= 0 && this.modal.style.display === 'block') {
                this.fermerModal();
            }
        });
    }

    afficher(morceauId, pubData = null) {
        this.morceauId = morceauId;
        this.countdown = 7;
        
        // Afficher la modal
        this.modal.style.display = 'block';
        document.body.style.overflow = 'hidden'; // Empêcher le scroll
        
        // Charger la publicité
        this.chargerPublicite(pubData);
        
        // Démarrer le countdown
        this.demarrerCountdown();
    }

    chargerPublicite(pubData) {
        const pubContent = document.getElementById('pub-content');
        
        if (pubData) {
            // Utiliser les données de pub fournies
            if (pubData.type === 'image' && pubData.image_url) {
                pubContent.innerHTML = `
                    <img src="${pubData.image_url}" alt="Publicité" class="pub-image">
                    ${pubData.lien ? `<a href="${pubData.lien}" target="_blank" class="pub-link">En savoir plus</a>` : ''}
                `;
            } else if (pubData.type === 'video' && pubData.video_url) {
                pubContent.innerHTML = `
                    <video controls class="pub-video">
                        <source src="${pubData.video_url}" type="video/mp4">
                        Votre navigateur ne supporte pas les vidéos.
                    </video>
                `;
            }
        } else {
            // Publicité par défaut (placeholder)
            pubContent.innerHTML = `
                <div class="pub-placeholder-default">
                    <h4>🎵 Badju's Records</h4>
                    <p>Découvrez la musique togolaise</p>
                    <div class="pub-animation">
                        <span class="pub-note">♪</span>
                        <span class="pub-note">♫</span>
                        <span class="pub-note">♪</span>
                    </div>
                </div>
            `;
        }
    }

    demarrerCountdown() {
        // Réinitialiser les boutons
        this.closeButton.disabled = true;
        this.telechargerButton.disabled = true;
        this.countdownElement.textContent = this.countdown;
        this.countdownCloseElement.textContent = this.countdown;
        
        this.countdownInterval = setInterval(() => {
            this.countdown--;
            this.countdownElement.textContent = this.countdown;
            this.countdownCloseElement.textContent = this.countdown;
            
            if (this.countdown <= 0) {
                clearInterval(this.countdownInterval);
                this.countdownTermine();
            }
        }, 1000);
    }

    countdownTermine() {
        // Activer les boutons
        this.closeButton.disabled = false;
        this.closeButton.innerHTML = 'Fermer';
        this.telechargerButton.disabled = false;
        
        // Mettre à jour le texte
        document.querySelector('.countdown-text').textContent = 'Vous pouvez maintenant télécharger';
        document.querySelector('.countdown-timer').innerHTML = '<span>✓</span><span>Prêt</span>';
    }

    async telecharger() {
        if (!this.morceauId) return;
        
        try {
            // Envoyer la requête POST pour enregistrer la vue de la pub
            const response = await fetch(`/engagement/telecharger/${this.morceauId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: 'pub_vue=true'
            });
            
            const data = await response.json();
            
            if (data.succes && data.url) {
                // Créer un lien temporaire pour le téléchargement
                const link = document.createElement('a');
                link.href = data.url;
                link.download = '';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                
                // Fermer la modal après un court délai
                setTimeout(() => this.fermerModal(), 1000);
            } else {
                console.error('Erreur lors du téléchargement:', data);
                alert('Une erreur est survenue lors du téléchargement.');
            }
        } catch (error) {
            console.error('Erreur:', error);
            alert('Une erreur est survenue. Veuillez réessayer.');
        }
    }

    fermerModal() {
        // Arrêter le countdown si en cours
        if (this.countdownInterval) {
            clearInterval(this.countdownInterval);
        }
        
        // Masquer la modal
        this.modal.style.display = 'none';
        document.body.style.overflow = ''; // Réactiver le scroll
        
        // Réinitialiser
        this.morceauId = null;
        this.morceauUrl = null;
        this.countdown = 7;
    }

    getCsrfToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return decodeURIComponent(value);
            }
        }
        return '';
    }
}

// Initialiser la modal quand le DOM est chargé
document.addEventListener('DOMContentLoaded', () => {
    window.modalPublicite = new ModalPublicite();
});

// Fonction globale pour ouvrir la modal (utilisée par les templates)
function ouvrirModalTelechargement(morceauId, pubData = null) {
    if (window.modalPublicite) {
        window.modalPublicite.afficher(morceauId, pubData);
    }
}
