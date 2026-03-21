
// Fonction de téléchargement simple et directe
function telechargerMorceauSimple(morceauId, urlFichier) {
    console.log('Téléchargement simple:', morceauId, urlFichier);
    
    // Créer un lien de téléchargement
    var lien = document.createElement('a');
    lien.href = urlFichier;
    lien.download = 'morceau_' + morceauId + '.mp3';
    lien.style.display = 'none';
    document.body.appendChild(lien);
    
    // Cliquer sur le lien
    lien.click();
    
    // Nettoyer
    setTimeout(function() {
        document.body.removeChild(lien);
    }, 1000);
    
    // Afficher un message
    if (typeof showToast === 'function') {
        showToast('📥 Téléchargement démarré !');
    } else {
        alert('📥 Téléchargement démarré !');
    }
}

// Fonction pour obtenir l'URL du morceau
function getUrlMorceau(morceauId) {
    fetch('/engagement/telecharger/' + morceauId + '/', {
        method: 'POST',
        headers: { 'X-CSRFToken': getCookie('csrftoken') },
        body: 'pub_vue=false'
    })
    .then(response => response.json())
    .then(data => {
        if (data.succes && data.url) {
            telechargerMorceauSimple(morceauId, data.url);
        } else {
            console.error('Erreur:', data.message || 'Erreur inconnue');
            if (typeof showToast === 'function') {
                showToast('❌ Erreur: ' + (data.message || 'Erreur inconnue'));
            } else {
                alert('❌ Erreur: ' + (data.message || 'Erreur inconnue'));
            }
        }
    })
    .catch(error => {
        console.error('Erreur réseau:', error);
        if (typeof showToast === 'function') {
            showToast('❌ Erreur réseau');
        } else {
            alert('❌ Erreur réseau');
        }
    });
}

// Fonction pour obtenir un cookie
function getCookie(name) {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
        var c = cookies[i].trim();
        if (c.startsWith(name + '=')) {
            return decodeURIComponent(c.substring(name.length + 1));
        }
    }
    return '';
}
