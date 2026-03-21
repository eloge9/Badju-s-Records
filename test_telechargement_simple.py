#!/usr/bin/env python
"""
Test simple du téléchargement
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'badjus_records.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import Client
from django.urls import reverse
from models_app.models import Morceau

def test_telechargement_simple():
    print("🔍 TEST DE TÉLÉCHARGEMENT SIMPLE")
    print("=" * 50)
    
    client = Client()
    
    # Vérifier s'il y a des morceaux
    morceaux = Morceau.objects.filter(statut='valide')
    print(f"📊 Morceaux trouvés: {morceaux.count()}")
    
    if morceaux.count() == 0:
        print("❌ Aucun morceau trouvé pour tester")
        return
    
    # Prendre le premier morceau
    morceau = morceaux.first()
    print(f"🎵 Test avec morceau: {morceau.titre}")
    print(f"📁 Fichier MP3: {morceau.fichier_mp3}")
    
    # Tester la route de téléchargement sans authentification
    try:
        response = client.post(f'/engagement/telecharger/{morceau.id}/', {'pub_vue': 'false'})
        print(f"📡 Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Réponse succès: {data}")
            if data.get('succes') and data.get('url'):
                print(f"📥 URL de téléchargement: {data['url']}")
                print("✅ Route de téléchargement fonctionne!")
                
                # Vérifier si le fichier existe
                if morceau.fichier_mp3 and hasattr(morceau.fichier_mp3, 'url'):
                    print(f"📂️ Fichier MP3 accessible: {morceau.fichier_mp3.url}")
                    print("✅ Fichier MP3 accessible!")
                else:
                    print("❌ Fichier MP3 non accessible")
            else:
                print(f"❌ Erreur dans réponse: {data}")
        else:
            print(f"❌ Erreur HTTP: {response.content}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def creer_fonction_telechargement():
    print("\n🛠️ CRÉATION FONCTION TÉLÉCHARGEMENT SIMPLE")
    print("=" * 50)
    
    code_js = '''
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
'''
    
    # Écrire le code dans un fichier temporaire
    with open('telechargement_simple.js', 'w', encoding='utf-8') as f:
        f.write(code_js)
    
    print("✅ Fichier telechargement_simple.js créé")
    print("📝 Code JavaScript généré")
    print("\n📋 INSTRUCTIONS:")
    print("1. Ajouter ce script dans votre template:")
    print("   <script src='/static/telechargement_simple.js'></script>")
    print("2. Modifier le bouton pour utiliser getUrlMorceau():")
    print("   onclick=\"getUrlMorceau({{ video.morceau.id }})\"")
    print("3. Ou intégrer directement le code dans la page")

if __name__ == '__main__':
    test_telechargement_simple()
    creer_fonction_telechargement()
    print("\n🏁 TESTS TERMINÉS")
    print("=" * 50)
