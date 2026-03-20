from django.shortcuts import render, get_object_or_404
from models_app.models import ProfilArtiste, Morceau, Video


def liste_artistes(request):
    artistes = ProfilArtiste.objects.filter(
        utilisateur__is_active=True
    ).order_by('nom_artiste')
    return render(request, 'artistes/liste.html', {'artistes': artistes})


def detail_artiste(request, id):
    artiste  = get_object_or_404(ProfilArtiste, id=id)
    morceaux = artiste.morceaux.filter(statut='valide').order_by('-points')
    videos   = artiste.videos.filter(statut='valide').order_by('-created_at')
    return render(request, 'artistes/detail.html', {
        'artiste':  artiste,
        'morceaux': morceaux,
        'videos':   videos,
    })