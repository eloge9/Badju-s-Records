from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from models_app.models import (
    Morceau, Video, Vote, Telechargement,
    VueVideo, LikeVideo, CommentaireVideo, Abonnement, ProfilArtiste, EcouteMorceau
)


@login_required
@require_POST
def voter(request, morceau_id):
    morceau   = get_object_or_404(Morceau, id=morceau_id, statut='valide')
    deja_vote = Vote.objects.filter(morceau=morceau, user=request.user).exists()

    if deja_vote:
        return JsonResponse({'succes': False, 'message': 'Vous avez déjà voté pour ce morceau.'})

    Vote.objects.create(morceau=morceau, user=request.user)
    morceau.points += 5
    morceau.save(update_fields=['points'])

    return JsonResponse({
        'succes':  True,
        'message': 'Vote enregistré !',
        'points':  morceau.points,
        'nb_votes': morceau.nb_votes(),
    })


@require_POST
def valider_telechargement(request, morceau_id):
    morceau = get_object_or_404(Morceau, id=morceau_id, statut='valide')
    pub_vue = request.POST.get('pub_vue') == 'true'
    ip      = request.META.get('REMOTE_ADDR', '0.0.0.0')

    Telechargement.objects.create(
        morceau    = morceau,
        user       = request.user if request.user.is_authenticated else None,
        ip_address = ip,
        pub_vue    = pub_vue,
    )

    # Ajouter des points pour le téléchargement
    points_bonus = 15 if pub_vue else 10  # Plus de points si pub vue
    morceau.points += points_bonus
    morceau.save(update_fields=['points'])

    return JsonResponse({
        'succes': True,
        'url':    morceau.fichier_mp3.url,
    })


@require_POST
def enregistrer_vue(request, video_id):
    video      = get_object_or_404(Video, id=video_id, statut='valide')
    session_id = request.session.session_key

    if not session_id:
        request.session.create()
        session_id = request.session.session_key

    deja_vue = VueVideo.objects.filter(
        video=video,
        session_id=session_id
    ).exists()

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

    return JsonResponse({'succes': True})


@login_required
@require_POST
def liker_video(request, video_id):
    video     = get_object_or_404(Video, id=video_id)
    deja_like = LikeVideo.objects.filter(video=video, user=request.user).exists()

    if deja_like:
        LikeVideo.objects.filter(video=video, user=request.user).delete()
        like = False
    else:
        LikeVideo.objects.create(video=video, user=request.user)
        like = True

    return JsonResponse({
        'succes':   True,
        'like':     like,
        'nb_likes': video.likes.count(),
    })


@login_required
@require_POST
def commenter_video(request, video_id):
    video   = get_object_or_404(Video, id=video_id)
    contenu = request.POST.get('contenu', '').strip()
    parent_id = request.POST.get('parent_id')

    if not contenu:
        return JsonResponse({'succes': False, 'message': 'Commentaire vide.'})

    if len(contenu) > 1000:
        return JsonResponse({'succes': False, 'message': 'Commentaire trop long.'})

    parent = None
    if parent_id:
        try:
            parent = CommentaireVideo.objects.get(id=parent_id, video=video)
        except CommentaireVideo.DoesNotExist:
            pass

    commentaire = CommentaireVideo.objects.create(
        video   = video,
        user    = request.user,
        contenu = contenu,
        parent  = parent,
    )

    return JsonResponse({
        'succes':    True,
        'id':        commentaire.id,
        'contenu':   commentaire.contenu,
        'username':  commentaire.user.username,
        'avatar':    commentaire.user.avatar.url if hasattr(commentaire.user, 'avatar') and commentaire.user.avatar else None,
        'date':      commentaire.created_at.strftime('%d/%m/%Y à %H:%M'),
        'est_reponse': parent is not None,
    })


def get_pub_telechargement(request):
    """Récupérer une publicité pour le téléchargement"""
    pub = Publicite.objects.filter(actif=True).order_by('?').first()
    
    if pub:
        return JsonResponse({
            'succes': True,
            'pub': {
                'id': pub.id,
                'annonceur': pub.annonceur,
                'image_url': pub.image.url if pub.image else None,
                'video_url': pub.video.url if pub.video else None,
                'duree_secondes': pub.duree_secondes,
                'url_cible': pub.url_cible,
            }
        })
    else:
        return JsonResponse({'succes': False})


@require_POST
def enregistrer_ecoute(request, morceau_id):
    """Enregistrer une écoute de morceau et ajouter des points"""
    morceau    = get_object_or_404(Morceau, id=morceau_id, statut='valide')
    session_id = request.session.session_key
    ip_address = request.META.get('REMOTE_ADDR', '0.0.0.0')
    duree      = request.POST.get('duree', 0)

    if not session_id:
        request.session.create()
        session_id = request.session.session_key

    # Vérifier si déjà écouté récemment (éviter les abus)
    from django.utils import timezone
    from datetime import timedelta
    limite = timezone.now() - timedelta(minutes=5)

    deja_ecoute = EcouteMorceau.objects.filter(
        morceau    = morceau,
        session_id = session_id,
        created_at__gte = limite
    ).exists()

    if not deja_ecoute:
        # Enregistrer l'écoute
        EcouteMorceau.objects.create(
            morceau    = morceau,
            user       = request.user if request.user.is_authenticated else None,
            session_id = session_id,
            ip_address = ip_address,
            duree      = int(duree) if duree else None
        )

        # Ajouter des points à l'artiste
        points_ecoute = 3  # 3 points par écoute
        morceau.points += points_ecoute
        morceau.save(update_fields=['points'])

        return JsonResponse({
            'succes': True,
            'points': points_ecoute,
            'message': f'Écoute enregistrée ! +{points_ecoute} points'
        })
    else:
        return JsonResponse({
            'succes': False,
            'message': 'Déjà compté récemment'
        })


@login_required
@require_POST
def abonner(request, artiste_id):
    artiste    = get_object_or_404(ProfilArtiste, id=artiste_id)
    abonnement = Abonnement.objects.filter(
                     abonne=request.user,
                     artiste=artiste
                 ).first()

    if abonnement:
        abonnement.delete()
        est_abonne = False
    else:
        Abonnement.objects.create(abonne=request.user, artiste=artiste)
        est_abonne = True

    return JsonResponse({
        'succes':      True,
        'est_abonne':  est_abonne,
        'nb_abonnes':  artiste.abonnes.count(),
    })