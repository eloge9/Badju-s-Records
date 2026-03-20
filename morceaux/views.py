from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from models_app.models import (
    Morceau, Video, Publicite,
    ProfilArtiste, Vote, Telechargement
)
from .forms import MorceauForm, VideoForm


# ─────────────────────────────────────────────
# ACCUEIL
# ─────────────────────────────────────────────

def accueil(request):
    top10    = Morceau.objects.filter(statut='valide').order_by('-points')[:10]
    nouveaux = Morceau.objects.filter(statut='valide').order_by('-created_at')[:8]
    videos   = Video.objects.filter(statut='valide').order_by('-created_at')[:6]
    return render(request, 'morceaux/accueil.html', {
        'top10':    top10,
        'nouveaux': nouveaux,
        'videos':   videos,
    })


# ─────────────────────────────────────────────
# TOP 100
# ─────────────────────────────────────────────

def top100(request):
    genre_filtre = request.GET.get('genre', '')
    morceaux = Morceau.objects.filter(statut='valide').order_by('-points')
    if genre_filtre:
        morceaux = morceaux.filter(genre=genre_filtre)
    morceaux = morceaux[:100]
    genres = Morceau.GENRES
    return render(request, 'morceaux/top100.html', {
        'morceaux':      morceaux,
        'genre_filtre':  genre_filtre,
        'genres':        genres,
    })


# ─────────────────────────────────────────────
# DÉTAIL MORCEAU
# ─────────────────────────────────────────────

def detail_morceau(request, id):
    morceau  = get_object_or_404(Morceau, id=id, statut='valide')
    pub      = Publicite.objects.filter(actif=True).order_by('?').first()
    autres   = Morceau.objects.filter(
        artiste=morceau.artiste,
        statut='valide'
    ).exclude(id=id)[:4]

    deja_vote = False
    if request.user.is_authenticated:
        deja_vote = Vote.objects.filter(
            morceau=morceau,
            user=request.user
        ).exists()

    return render(request, 'morceaux/detail.html', {
        'morceau':   morceau,
        'pub':       pub,
        'autres':    autres,
        'deja_vote': deja_vote,
    })


# ─────────────────────────────────────────────
# BADJU TV
# ─────────────────────────────────────────────

def badju_tv(request):
    artiste_filtre = request.GET.get('artiste', '')
    videos = Video.objects.filter(statut='valide').order_by('-created_at')
    if artiste_filtre:
        videos = videos.filter(artiste__nom_artiste__icontains=artiste_filtre)
    return render(request, 'morceaux/tv.html', {
        'videos':          videos,
        'artiste_filtre':  artiste_filtre,
    })


# ─────────────────────────────────────────────
# DASHBOARD ARTISTE
# ─────────────────────────────────────────────

@login_required
def dashboard_artiste(request):
    if request.user.role != 'artiste':
        messages.error(request, "Accès réservé aux artistes.")
        return redirect('accueil')

    try:
        artiste = request.user.profil_artiste
    except ProfilArtiste.DoesNotExist:
        messages.error(request, "Profil artiste introuvable.")
        return redirect('accueil')

    morceaux = artiste.morceaux.all().order_by('-created_at')
    videos   = artiste.videos.all().order_by('-created_at')

    return render(request, 'morceaux/dashboard.html', {
        'artiste':  artiste,
        'morceaux': morceaux,
        'videos':   videos,
    })


# ─────────────────────────────────────────────
# AJOUTER MORCEAU
# ─────────────────────────────────────────────

@login_required
def ajouter_morceau(request):
    if request.user.role != 'artiste':
        messages.error(request, "Accès réservé aux artistes.")
        return redirect('accueil')

    try:
        artiste = request.user.profil_artiste
    except ProfilArtiste.DoesNotExist:
        return redirect('accueil')

    if request.method == 'POST':
        form = MorceauForm(request.POST, request.FILES)
        if form.is_valid():
            morceau         = form.save(commit=False)
            morceau.artiste = artiste
            morceau.statut  = 'en_attente'
            morceau.save()
            messages.success(request, f"'{morceau.titre}' soumis avec succès. En attente de validation.")
            return redirect('dashboard')
        else:
            messages.error(request, "Veuillez corriger les erreurs.")
    else:
        form = MorceauForm()

    return render(request, 'morceaux/form_morceau.html', {'form': form, 'action': 'Ajouter'})


# ─────────────────────────────────────────────
# MODIFIER MORCEAU
# ─────────────────────────────────────────────

@login_required
def modifier_morceau(request, id):
    if request.user.role != 'artiste':
        return redirect('accueil')

    try:
        artiste = request.user.profil_artiste
    except ProfilArtiste.DoesNotExist:
        return redirect('accueil')

    morceau = get_object_or_404(Morceau, id=id, artiste=artiste)

    if request.method == 'POST':
        form = MorceauForm(request.POST, request.FILES, instance=morceau)
        if form.is_valid():
            form.save()
            messages.success(request, f"'{morceau.titre}' modifié avec succès.")
            return redirect('dashboard')
        else:
            messages.error(request, "Veuillez corriger les erreurs.")
    else:
        form = MorceauForm(instance=morceau)

    return render(request, 'morceaux/form_morceau.html', {'form': form, 'action': 'Modifier'})


# ─────────────────────────────────────────────
# SUPPRIMER MORCEAU
# ─────────────────────────────────────────────

@login_required
def supprimer_morceau(request, id):
    if request.user.role != 'artiste':
        return redirect('accueil')

    try:
        artiste = request.user.profil_artiste
    except ProfilArtiste.DoesNotExist:
        return redirect('accueil')

    morceau = get_object_or_404(Morceau, id=id, artiste=artiste)

    if request.method == 'POST':
        titre = morceau.titre
        morceau.delete()
        messages.success(request, f"'{titre}' supprimé avec succès.")
        return redirect('dashboard')

    return render(request, 'morceaux/confirmer_suppression.html', {'morceau': morceau})


# ─────────────────────────────────────────────
# AJOUTER VIDÉO
# ─────────────────────────────────────────────

@login_required
def ajouter_video(request):
    if request.user.role != 'artiste':
        messages.error(request, "Accès réservé aux artistes.")
        return redirect('accueil')

    try:
        artiste = request.user.profil_artiste
    except ProfilArtiste.DoesNotExist:
        return redirect('accueil')

    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES, artiste=artiste)
        if form.is_valid():
            video         = form.save(commit=False)
            video.artiste = artiste
            video.statut  = 'en_attente'
            video.save()
            messages.success(request, f"'{video.titre}' soumise avec succès. En attente de validation.")
            return redirect('dashboard')
        else:
            messages.error(request, "Veuillez corriger les erreurs.")
    else:
        form = VideoForm(artiste=artiste)

    return render(request, 'morceaux/form_video.html', {'form': form})