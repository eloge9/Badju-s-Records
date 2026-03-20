from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from models_app.models import (
    Morceau, Video, Publicite,
    ProfilArtiste, Vote, Telechargement, VueVideo, LikeVideo, CommentaireVideo
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
    recherche = request.GET.get('recherche', '')
    videos = Video.objects.filter(statut='valide').order_by('-created_at')
    
    if recherche:
        # Recherche multi-critères
        videos = videos.filter(
            Q(titre__icontains=recherche) |
            Q(artiste__nom_artiste__icontains=recherche) |
            Q(morceau__genre__icontains=recherche) |
            Q(morceau__genre_display__icontains=recherche)
        ).distinct()
    
    return render(request, 'morceaux/tv.html', {
        'videos': videos,
        'recherche': recherche,
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
            try:
                morceau = form.save(commit=False)
                morceau.artiste = artiste
                morceau.statut = 'valide'  # Validé automatiquement
                morceau.save()
                
                messages.success(
                    request, 
                    f"🎵 '{morceau.titre}' publié avec succès ! "
                    "Votre morceau est maintenant disponible sur Badju's Records."
                )
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f"Une erreur est survenue: {str(e)}")
                print(f"Erreur lors de la sauvegarde du morceau: {e}")
        else:
            messages.error(request, "❌ Veuillez corriger les erreurs ci-dessous:")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"• {field}: {error}")
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
            video.statut  = 'valide'  # Validé automatiquement
            video.save()
            messages.success(
                request, 
                f"🎬 '{video.titre}' publiée avec succès ! "
                "Votre vidéo est maintenant disponible sur Badju's Records."
            )
            return redirect('dashboard')
        else:
            messages.error(request, "❌ Veuillez corriger les erreurs ci-dessous:")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"• {field}: {error}")
    else:
        form = VideoForm(artiste=artiste)

    return render(request, 'morceaux/form_video.html', {'form': form})


# ─────────────────────────────────────────────
# DÉTAIL VIDÉO
# ─────────────────────────────────────────────

def detail_video(request, id):
    video = get_object_or_404(Video, id=id, statut='valide')
    videos_similaires = Video.objects.filter(
        statut='valide'
    ).exclude(id=id).order_by('-created_at')[:10]
    
    # Enregistrer la vue
    session_id = request.session.session_key
    if not session_id:
        request.session.create()
        session_id = request.session.session_key

    deja_vue = VueVideo.objects.filter(video=video, session_id=session_id).exists()
    if not deja_vue:
        VueVideo.objects.create(
            video      = video,
            user       = request.user if request.user.is_authenticated else None,
            session_id = session_id,
        )
        video.nb_vues += 1
        video.save(update_fields=['nb_vues'])
        if video.morceau:
            video.morceau.points += 2
            video.morceau.save(update_fields=['points'])

    # Vérifier si déjà liké
    deja_like = False
    if request.user.is_authenticated:
        deja_like = LikeVideo.objects.filter(video=video, user=request.user).exists()

    commentaires = video.commentaires.filter(parent=None).order_by('-created_at')

    return render(request, 'morceaux/detail_video.html', {
        'video':            video,
        'videos_similaires': videos_similaires,
        'deja_like':        deja_like,
        'commentaires':     commentaires,
    })