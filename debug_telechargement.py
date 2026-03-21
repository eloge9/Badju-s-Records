#!/usr/bin/env python
"""
Script de test pour le téléchargement
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

def test_telechargement():
    print("🔍 TEST DE TÉLÉCHARGEMENT")
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
    
    # Tester la route de téléchargement
    try:
        response = client.post(f'/engagement/telecharger/{morceau.id}/', {'pub_vue': 'false'})
        print(f"📡 Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Réponse succès: {data}")
            if data.get('succes') and data.get('url'):
                print(f"📥 URL de téléchargement: {data['url']}")
                print("✅ Téléchargement fonctionne!")
            else:
                print(f"❌ Erreur dans réponse: {data}")
        else:
            print(f"❌ Erreur HTTP: {response.content}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

def test_template():
    print("\n🔍 TEST DU TEMPLATE")
    print("=" * 50)
    
    # Vérifier le template
    template_file = 'templates/morceaux/detail_video.html'
    if os.path.exists(template_file):
        with open(template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Chercher la fonction telechargerSon
        if 'function telechargerSon(' in content:
            print("✅ Fonction telechargerSon trouvée")
        else:
            print("❌ Fonction telechargerSon non trouvée")
        
        # Chercher le bouton
        if 'btn-telecharger-son' in content:
            print("✅ Bouton btn-telecharger-son trouvé")
        else:
            print("❌ Bouton btn-telecharger-son non trouvé")
            
        # Chercher les erreurs JavaScript
        if 'id: {{ video.morceau.id }' in content:
            print("❌ Erreur JavaScript détectée: parenthèse manquante")
        else:
            print("✅ Pas d'erreur JavaScript évidente")
    else:
        print(f"❌ Template non trouvé: {template_file}")

if __name__ == '__main__':
    test_telechargement()
    test_template()
    print("\n🏁 TESTS TERMINÉS")
    print("=" * 50)
