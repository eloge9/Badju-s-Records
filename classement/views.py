from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from django.contrib import messages
from models_app.models import Morceau, Telechargement, Vote, VueVideo


@staff_member_required
def recalculer(request):
    morceaux = Morceau.objects.filter(statut='valide')

    for morceau in morceaux:
        nb_dl    = Telechargement.objects.filter(morceau=morceau, pub_vue=True).count()
        nb_votes = Vote.objects.filter(morceau=morceau).count()
        nb_vues  = VueVideo.objects.filter(video__morceau=morceau).count()
        morceau.points = (nb_dl * 10) + (nb_votes * 5) + (nb_vues * 2)
        morceau.save(update_fields=['points'])

    # Recalcul des rangs
    morceaux_tries = Morceau.objects.filter(statut='valide').order_by('-points')
    for rang, morceau in enumerate(morceaux_tries, start=1):
        morceau.rang = rang
        morceau.save(update_fields=['rang'])

    messages.success(request, f"Classement recalculé — {morceaux_tries.count()} morceaux mis à jour.")
    return redirect('/admin/')