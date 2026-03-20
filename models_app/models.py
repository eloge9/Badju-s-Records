from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
import uuid
import os


# ─────────────────────────────────────────────
# VALIDATEURS
# ─────────────────────────────────────────────

def valider_image(fichier):
    ext = os.path.splitext(fichier.name)[1].lower().replace('.', '')
    if ext not in ['jpg', 'jpeg', 'png', 'webp']:
        raise ValidationError(f"Format non autorisé : .{ext} — Acceptés : jpg, jpeg, png, webp")

def valider_audio(fichier):
    ext = os.path.splitext(fichier.name)[1].lower().replace('.', '')
    if ext not in ['mp3', 'wav', 'ogg']:
        raise ValidationError(f"Format non autorisé : .{ext} — Acceptés : mp3, wav, ogg")

def valider_video(fichier):
    ext = os.path.splitext(fichier.name)[1].lower().replace('.', '')
    if ext not in ['mp4', 'webm', 'mov']:
        raise ValidationError(f"Format non autorisé : .{ext} — Acceptés : mp4, webm, mov")

def chemin_avatar(instance, filename):
    ext = os.path.splitext(filename)[1]
    return f"avatars/{instance.id}{ext}"


# ─────────────────────────────────────────────
# UTILISATEUR DE BASE
# Un seul AbstractUser, tous les acteurs
# partagent ce compte
# ─────────────────────────────────────────────

class User(AbstractUser):
    ROLE_CHOICES = (
        ('utilisateur',    'Utilisateur'),
        ('artiste',        'Artiste'),
        ('administrateur', 'Administrateur'),
    )

    id       = models.UUIDField(
                   primary_key=True,
                   default=uuid.uuid4,
                   editable=False
               )
    email    = models.EmailField(unique=True)
    role     = models.CharField(
                   max_length=20,
                   choices=ROLE_CHOICES,
                   default='utilisateur'
               )
    avatar   = models.ImageField(
                   upload_to=chemin_avatar,
                   blank=True,
                   null=True,
                   validators=[valider_image]
               )
    pays     = models.CharField(max_length=60, blank=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)

    USERNAME_FIELD  = 'username'
    REQUIRED_FIELDS = ['email', 'role']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    def est_utilisateur(self):
        return self.role == 'utilisateur'

    def est_artiste(self):
        return self.role == 'artiste'

    def est_admin(self):
        return self.role == 'administrateur' or self.is_staff


# ─────────────────────────────────────────────
# PROFIL UTILISATEUR
# Champs spécifiques à l'utilisateur standard
# ─────────────────────────────────────────────

class ProfilUtilisateur(models.Model):
    utilisateur   = models.OneToOneField(
                        User,
                        on_delete=models.CASCADE,
                        related_name='profil_utilisateur'
                    )
    bio_courte    = models.CharField(max_length=160, blank=True)
    date_naissance = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'profils_utilisateurs'

    def __str__(self):
        return f"Profil Utilisateur : {self.utilisateur.username}"

    def total_votes_donnes(self):
        return Vote.objects.filter(user=self.utilisateur).count()

    def total_telechargements(self):
        return Telechargement.objects.filter(
            user=self.utilisateur,
            pub_vue=True
        ).count()


# ─────────────────────────────────────────────
# PROFIL ARTISTE
# Champs spécifiques à l'artiste
# Un artiste a aussi toutes les fonctions
# d'un utilisateur standard
# ─────────────────────────────────────────────

class ProfilArtiste(models.Model):
    GENRES = [
        ('afrobeat',     'Afrobeat'),
        ('trap',         'Trap'),
        ('rnb',          'RnB'),
        ('gospel',       'Gospel'),
        ('coupe-decale', 'Coupé-Décalé'),
        ('hiphop',       'Hip-Hop'),
        ('pop',          'Pop'),
        ('autre',        'Autre'),
    ]

    utilisateur = models.OneToOneField(
                      User,
                      on_delete=models.CASCADE,
                      related_name='profil_artiste'
                  )
    nom_artiste = models.CharField(max_length=100)
    bio         = models.TextField(blank=True)
    photo       = models.ImageField(
                      upload_to='artistes/photos/',
                      null=True,
                      blank=True,
                      validators=[valider_image]
                  )
    photo_cover = models.ImageField(
                      upload_to='artistes/covers/',
                      null=True,
                      blank=True,
                      validators=[valider_image]
                  )
    genre       = models.CharField(
                      max_length=50,
                      choices=GENRES,
                      blank=True
                  )
    ville       = models.CharField(max_length=100, blank=True)
    facebook    = models.URLField(blank=True)
    instagram   = models.URLField(blank=True)
    twitter     = models.URLField(blank=True)
    verified    = models.BooleanField(
                      default=False,
                      help_text='Vérifié par un administrateur'
                  )

    class Meta:
        db_table = 'profils_artistes'
        ordering = ['nom_artiste']

    def __str__(self):
        return f"Profil Artiste : {self.nom_artiste}"

    def total_morceaux(self):
        return self.morceaux.filter(statut='valide').count()

    def total_telechargements(self):
        return Telechargement.objects.filter(
            morceau__artiste=self,
            pub_vue=True
        ).count()

    def total_votes(self):
        return Vote.objects.filter(
            morceau__artiste=self
        ).count()

    def total_vues(self):
        return VueVideo.objects.filter(
            video__artiste=self
        ).count()

    def meilleur_rang(self):
        morceaux = self.morceaux.filter(
            statut='valide',
            rang__isnull=False
        ).order_by('rang')
        if morceaux.exists():
            return morceaux.first().rang
        return None


# ─────────────────────────────────────────────
# PROFIL ADMINISTRATEUR
# Champs spécifiques à l'admin
# Un admin peut créer un autre admin
# ─────────────────────────────────────────────

class ProfilAdministrateur(models.Model):
    NIVEAUX = [
        ('super',    'Super Administrateur'),
        ('standard', 'Administrateur Standard'),
    ]

    utilisateur = models.OneToOneField(
                      User,
                      on_delete=models.CASCADE,
                      related_name='profil_admin'
                  )
    niveau      = models.CharField(
                      max_length=10,
                      choices=NIVEAUX,
                      default='standard'
                  )
    cree_par    = models.ForeignKey(
                      'self',
                      on_delete=models.SET_NULL,
                      null=True,
                      blank=True,
                      related_name='admins_crees',
                      help_text='Admin qui a créé ce compte'
                  )
    service     = models.CharField(
                      max_length=100,
                      blank=True,
                      help_text='Service ou département'
                  )

    class Meta:
        db_table = 'profils_administrateurs'

    def __str__(self):
        return f"Profil Admin : {self.utilisateur.username} ({self.get_niveau_display()})"

    def creer_admin(self, username, email, password, niveau='standard'):
        """
        Crée un nouvel administrateur.
        Seul un admin existant peut appeler cette méthode.
        """
        nouvel_user = User.objects.create_user(
            username = username,
            email    = email,
            password = password,
            role     = 'administrateur',
            is_staff = True,
        )
        nouvel_profil = ProfilAdministrateur.objects.create(
            utilisateur = nouvel_user,
            niveau      = niveau,
            cree_par    = self,
        )
        return nouvel_profil


# ─────────────────────────────────────────────
# MORCEAU
# ─────────────────────────────────────────────

class Morceau(models.Model):
    STATUTS = [
        ('en_attente', 'En attente'),
        ('valide',     'Validé'),
        ('refuse',     'Refusé'),
    ]
    GENRES = [
        ('afrobeat',     'Afrobeat'),
        ('trap',         'Trap'),
        ('rnb',          'RnB'),
        ('gospel',       'Gospel'),
        ('coupe-decale', 'Coupé-Décalé'),
        ('hiphop',       'Hip-Hop'),
        ('pop',          'Pop'),
        ('autre',        'Autre'),
    ]

    artiste     = models.ForeignKey(
                      ProfilArtiste,
                      on_delete=models.CASCADE,
                      related_name='morceaux'
                  )
    titre       = models.CharField(max_length=200)
    genre       = models.CharField(max_length=30, choices=GENRES)
    pochette    = models.ImageField(
                      upload_to='morceaux/pochettes/',
                      validators=[valider_image]
                  )
    fichier_mp3 = models.FileField(
                      upload_to='morceaux/audio/',
                      validators=[valider_audio]
                  )
    duree       = models.PositiveIntegerField(
                      default=0,
                      help_text='Durée en secondes'
                  )
    points      = models.PositiveIntegerField(default=0)
    rang        = models.PositiveIntegerField(null=True, blank=True)
    statut      = models.CharField(
                      max_length=20,
                      choices=STATUTS,
                      default='en_attente'
                  )
    date_sortie = models.DateField()
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'morceaux'
        ordering = ['-points']

    def __str__(self):
        return f"{self.titre} — {self.artiste.nom_artiste}"

    def nb_telechargements(self):
        return self.telechargement_set.filter(pub_vue=True).count()

    def nb_votes(self):
        return self.vote_set.count()

    def duree_formatee(self):
        minutes  = self.duree // 60
        secondes = self.duree % 60
        return f"{minutes}:{secondes:02d}"


# ─────────────────────────────────────────────
# VIDÉO
# ─────────────────────────────────────────────

class Video(models.Model):
    STATUTS = [
        ('en_attente', 'En attente'),
        ('valide',     'Validé'),
        ('refuse',     'Refusé'),
    ]

    artiste       = models.ForeignKey(
                        ProfilArtiste,
                        on_delete=models.CASCADE,
                        related_name='videos'
                    )
    morceau       = models.ForeignKey(
                        Morceau,
                        on_delete=models.SET_NULL,
                        null=True,
                        blank=True,
                        related_name='videos'
                    )
    titre         = models.CharField(max_length=200)
    fichier_video = models.FileField(
                        upload_to='morceaux/videos/',
                        null=True,
                        blank=True,
                        validators=[valider_video]
                    )
    youtube_url   = models.URLField(
                        blank=True,
                        help_text='Lien YouTube si pas de fichier local'
                    )
    thumbnail     = models.ImageField(
                        upload_to='morceaux/thumbnails/',
                        null=True,
                        blank=True,
                        validators=[valider_image]
                    )
    nb_vues       = models.PositiveIntegerField(default=0)
    statut        = models.CharField(
                        max_length=20,
                        choices=STATUTS,
                        default='en_attente'
                    )
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'videos'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.titre} — {self.artiste.nom_artiste}"

    def est_youtube(self):
        return bool(self.youtube_url) and not self.fichier_video

    def youtube_embed_url(self):
        if not self.youtube_url:
            return ''
        if 'watch?v=' in self.youtube_url:
            video_id = self.youtube_url.split('watch?v=')[-1].split('&')[0]
            return f"https://www.youtube.com/embed/{video_id}"
        if 'youtu.be/' in self.youtube_url:
            video_id = self.youtube_url.split('youtu.be/')[-1].split('?')[0]
            return f"https://www.youtube.com/embed/{video_id}"
        return self.youtube_url


# ─────────────────────────────────────────────
# TÉLÉCHARGEMENT
# ─────────────────────────────────────────────

class Telechargement(models.Model):
    morceau    = models.ForeignKey(
                     Morceau,
                     on_delete=models.CASCADE
                 )
    user       = models.ForeignKey(
                     User,
                     on_delete=models.SET_NULL,
                     null=True,
                     blank=True
                 )
    ip_address = models.GenericIPAddressField()
    pub_vue    = models.BooleanField(
                     default=False,
                     help_text='Publicité regardée jusqu\'au bout'
                 )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'telechargements'
        ordering = ['-created_at']

    def __str__(self):
        return f"Téléchargement — {self.morceau.titre}"


# ─────────────────────────────────────────────
# VOTE
# ─────────────────────────────────────────────

class Vote(models.Model):
    morceau    = models.ForeignKey(
                     Morceau,
                     on_delete=models.CASCADE
                 )
    user       = models.ForeignKey(
                     User,
                     on_delete=models.CASCADE
                 )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'votes'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['morceau', 'user'],
                name='un_vote_par_user_par_morceau'
            )
        ]

    def __str__(self):
        return f"{self.user.username} → {self.morceau.titre}"


# ─────────────────────────────────────────────
# VUE VIDÉO
# ─────────────────────────────────────────────

class VueVideo(models.Model):
    video      = models.ForeignKey(
                     Video,
                     on_delete=models.CASCADE
                 )
    user       = models.ForeignKey(
                     User,
                     on_delete=models.SET_NULL,
                     null=True,
                     blank=True
                 )
    session_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'vues_video'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['video', 'session_id'],
                name='une_vue_par_session_par_video'
            )
        ]

    def __str__(self):
        return f"Vue — {self.video.titre}"


# ─────────────────────────────────────────────
# CERTIFICATION
# ─────────────────────────────────────────────

class Certification(models.Model):
    NIVEAUX = [
        ('or',      'Or'),
        ('platine', 'Platine'),
        ('diamant', 'Diamant'),
    ]
    SEUILS = {
        'or':      1000,
        'platine': 5000,
        'diamant': 10000,
    }

    morceau    = models.OneToOneField(
                     Morceau,
                     on_delete=models.CASCADE,
                     related_name='certification'
                 )
    niveau     = models.CharField(max_length=20, choices=NIVEAUX)
    valide_par = models.ForeignKey(
                     ProfilAdministrateur,
                     on_delete=models.SET_NULL,
                     null=True
                 )
    date       = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'certifications'

    def __str__(self):
        return f"{self.morceau.titre} — {self.get_niveau_display()}"


# ─────────────────────────────────────────────
# PUBLICITÉ
# ─────────────────────────────────────────────

class Publicite(models.Model):
    annonceur      = models.CharField(max_length=100)
    image          = models.ImageField(
                         upload_to='publicites/',
                         null=True,
                         blank=True,
                         validators=[valider_image]
                     )
    video          = models.FileField(
                         upload_to='publicites/videos/',
                         null=True,
                         blank=True,
                         validators=[valider_video]
                     )
    url_cible      = models.URLField(
                         blank=True,
                         help_text='URL de redirection au clic sur la pub'
                     )
    duree_secondes = models.PositiveSmallIntegerField(
                         default=7,
                         help_text='Secondes à attendre avant de télécharger'
                     )
    actif          = models.BooleanField(default=True)
    nb_affichages  = models.PositiveIntegerField(default=0)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'publicites'
        ordering = ['-created_at']

    def __str__(self):
        return f"Pub — {self.annonceur}"

    def clean(self):
        if not self.image and not self.video:
            raise ValidationError(
                "Une publicité doit avoir au moins une image ou une vidéo."
            )
