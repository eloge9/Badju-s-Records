from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import (
    InscriptionForm,
    ConnexionForm,
    ModifierProfilForm,
    ModifierProfilArtisteForm,
    CreerProfilArtisteForm,
)
from models_app.models import (
    User, ProfilUtilisateur, ProfilArtiste,
    Vote, Telechargement, Abonnement
)


# ─────────────────────────────────────────────
# INSCRIPTION
# ─────────────────────────────────────────────

def inscription(request):
    # Rediriger si déjà connecté
    if request.user.is_authenticated:
        return redirect('accueil')

    if request.method == 'POST':
        form = InscriptionForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # Connecter automatiquement après inscription
            login(request, user)
            messages.success(request, f"Bienvenue {user.username} ! Votre compte a été créé avec succès.")
            return redirect('mon_espace')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = InscriptionForm()

    return render(request, 'users/inscription.html', {'form': form})


# ─────────────────────────────────────────────
# CONNEXION
# ─────────────────────────────────────────────

def connexion(request):
    # Rediriger si déjà connecté
    if request.user.is_authenticated:
        return _rediriger_selon_role(request.user)

    if request.method == 'POST':
        form = ConnexionForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bon retour {user.username} !")
            return _rediriger_selon_role(user)
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = ConnexionForm()

    return render(request, 'users/connexion.html', {'form': form})


def _rediriger_selon_role(user):
    """
    Redirige l'utilisateur vers la bonne page selon son rôle.
    """
    if user.role == 'administrateur' or user.is_staff:
        return redirect('/admin/')
    elif user.role == 'artiste':
        return redirect('dashboard')
    else:
        return redirect('mon_espace')


# ─────────────────────────────────────────────
# DÉCONNEXION
# ─────────────────────────────────────────────

def deconnexion(request):
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect('accueil')


# ─────────────────────────────────────────────
# MON ESPACE — Espace utilisateur standard
# ─────────────────────────────────────────────

@login_required
def mon_espace(request):
    user   = request.user
    profil, created = ProfilUtilisateur.objects.get_or_create(utilisateur=user)

    votes           = Vote.objects.filter(user=user).select_related('morceau').order_by('-created_at')
    telechargements = Telechargement.objects.filter(user=user).select_related('morceau').order_by('-created_at')
    abonnements     = Abonnement.objects.filter(abonne=user).select_related('artiste').order_by('-created_at')

    context = {
        'user':               user,
        'profil':             profil,
        'votes':              votes,
        'telechargements':    telechargements,
        'abonnements':        abonnements,
        'nb_votes':           votes.count(),
        'nb_telechargements': telechargements.count(),
        'nb_abonnements':     abonnements.count(),
        'peut_devenir_artiste': user.role == 'utilisateur',
    }
    return render(request, 'users/mon_espace.html', context)


# ─────────────────────────────────────────────
# DEVENIR ARTISTE
# Un utilisateur crée son profil artiste
# ─────────────────────────────────────────────

@login_required
def devenir_artiste(request):
    user = request.user

    # Seul un utilisateur standard peut devenir artiste
    if user.role != 'utilisateur':
        if user.role == 'artiste':
            messages.info(request, "Vous avez déjà un profil artiste.")
            return redirect('dashboard')
        else:
            messages.error(request, "Action non autorisée.")
            return redirect('accueil')

    if request.method == 'POST':
        form = CreerProfilArtisteForm(request.POST, request.FILES)
        if form.is_valid():
            profil_artiste             = form.save(commit=False)
            profil_artiste.utilisateur = user
            profil_artiste.save()

            # Changer le rôle de l'utilisateur en artiste
            user.role = 'artiste'
            user.save(update_fields=['role'])

            messages.success(
                request,
                f"Félicitations {profil_artiste.nom_artiste} ! "
                f"Votre profil artiste a été créé. Bienvenue sur Badju's Records !"
            )
            return redirect('dashboard')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = CreerProfilArtisteForm()

    return render(request, 'users/devenir_artiste.html', {
        'form': form,
        'genres': Morceau.GENRES
    })


# ─────────────────────────────────────────────
# MODIFIER PROFIL
# ─────────────────────────────────────────────

@login_required
def modifier_profil(request):
    user = request.user

    # Préparer le formulaire artiste si besoin
    form_artiste = None
    profil_artiste = None
    if user.role == 'artiste':
        try:
            profil_artiste = user.profil_artiste
        except ProfilArtiste.DoesNotExist:
            profil_artiste = None

    if request.method == 'POST':
        # Formulaire compte principal
        form = ModifierProfilForm(
            request.POST,
            request.FILES,
            instance=user
        )

        # Formulaire profil artiste si artiste
        if profil_artiste:
            form_artiste = ModifierProfilArtisteForm(
                request.POST,
                request.FILES,
                instance=profil_artiste,
                prefix='artiste'
            )

        # Valider les deux formulaires
        form_valide         = form.is_valid()
        form_artiste_valide = (form_artiste.is_valid() if form_artiste else True)

        if form_valide and form_artiste_valide:
            form.save()
            if form_artiste:
                form_artiste.save()
            messages.success(request, "Profil mis à jour avec succès !")
            if user.role == 'artiste':
                return redirect('dashboard')
            return redirect('mon_espace')
        else:
            messages.error(request, "Veuillez corriger les erreurs.")
    else:
        form = ModifierProfilForm(instance=user)
        if profil_artiste:
            form_artiste = ModifierProfilArtisteForm(
                instance=profil_artiste,
                prefix='artiste'
            )

    return render(request, 'users/modifier_profil.html', {
        'form':         form,
        'form_artiste': form_artiste,
        'user':         user,
    })


# ─────────────────────────────────────────────
# PROFIL PUBLIC UTILISATEUR
# ─────────────────────────────────────────────

def profil_public(request, username):
    profil_user = get_object_or_404(User, username=username, is_active=True)

    # Si c'est un artiste, rediriger vers son profil artiste
    if profil_user.role == 'artiste':
        try:
            return redirect('detail_artiste', id=profil_user.profil_artiste.id)
        except:
            pass

    votes          = Vote.objects.filter(user=profil_user).select_related('morceau').order_by('-created_at')[:10]
    telechargements = Telechargement.objects.filter(
        user=profil_user, pub_vue=True
    ).select_related('morceau').order_by('-created_at')[:10]

    return render(request, 'users/profil_public.html', {
        'profil_user':    profil_user,
        'votes':          votes,
        'telechargements': telechargements,
        'nb_votes':       Vote.objects.filter(user=profil_user).count(),
        'nb_dl':          Telechargement.objects.filter(user=profil_user, pub_vue=True).count(),
    })


# ─────────────────────────────────────────────
# NOTIFICATIONS
# ─────────────────────────────────────────────

@login_required
def notifications(request):
    notifs = request.user.notifications.all()[:30]
    # Marquer toutes comme lues
    request.user.notifications.filter(lu=False).update(lu=True)
    return render(request, 'users/notifications.html', {'notifs': notifs})

@login_required
def nb_notifications_non_lues(request):
    nb = request.user.notifications.filter(lu=False).count()
    return JsonResponse({'nb': nb})