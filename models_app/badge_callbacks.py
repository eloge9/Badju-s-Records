from models_app.models import Morceau, Video

def morceaux_en_attente(request):
    nb = Morceau.objects.filter(statut='en_attente').count()
    return str(nb) if nb > 0 else None

def videos_en_attente(request):
    nb = Video.objects.filter(statut='en_attente').count()
    return str(nb) if nb > 0 else None
