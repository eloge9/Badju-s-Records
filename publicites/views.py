from django.http import JsonResponse
from models_app.models import Publicite


def pub_aleatoire(request):
    pub = Publicite.objects.filter(actif=True).order_by('?').first()
    
    if not pub:
        # Retourner une pub par défaut si aucune pub n'existe
        return JsonResponse({
            'id': 0,
            'image': None,
            'video': None,
            'url_cible': None,
            'duree_secondes': 7,  # Durée par défaut
        })

    # Incrémenter le compteur d'affichages
    pub.nb_affichages += 1
    pub.save(update_fields=['nb_affichages'])

    return JsonResponse({
        'id':             pub.id,
        'image':          pub.image.url if pub.image else None,
        'video':          pub.video.url if pub.video else None,
        'url_cible':      pub.url_cible,
        'duree_secondes': pub.duree_secondes,
    })