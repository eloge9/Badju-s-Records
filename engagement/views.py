from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from models_app.models import Morceau, Video, Vote, Telechargement, VueVideo, LikeVideo, CommentaireVideo, Publicite


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

    if pub_vue:
        morceau.points += 10
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