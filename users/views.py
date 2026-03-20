from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from models_app.models import ProfilArtiste, Morceau, Vote, Telechargement
from .forms import (
    InscriptionForm,
    ConnexionForm,
    ModifierProfilForm,
    CreerProfilArtisteForm
)
from models_app.models import (
    User,
    ProfilUtilisateur,
    ProfilArtiste,
    Vote,
    Telechargement
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
    user = request.user

    # Récupérer ou créer le profil utilisateur si inexistant
    profil, created = ProfilUtilisateur.objects.get_or_create(
        utilisateur=user
    )

    # Statistiques de l'utilisateur
    votes          = Vote.objects.filter(user=user).select_related('morceau').order_by('-created_at')
    telechargements = Telechargement.objects.filter(
        user=user,
        pub_vue=True
    ).select_related('morceau').order_by('-created_at')

    context = {
        'user':             user,
        'profil':           profil,
        'votes':            votes,
        'telechargements':  telechargements,
        'nb_votes':         votes.count(),
        'nb_telechargements': telechargements.count(),
        # Afficher le bouton "Devenir Artiste" seulement si utilisateur standard
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

    if request.method == 'POST':
        form = ModifierProfilForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre profil a été mis à jour avec succès.")

            # Rediriger selon le rôle
            if user.role == 'artiste':
                return redirect('dashboard')
            return redirect('mon_espace')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = ModifierProfilForm(instance=user)

    return render(request, 'users/modifier_profil.html', {
        'form': form,
        'user': user,
    })