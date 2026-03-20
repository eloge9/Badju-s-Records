from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import (
    User,
    ProfilUtilisateur,
    ProfilArtiste,
    ProfilAdministrateur,
    Morceau,
    Video,
    Telechargement,
    Vote,
    VueVideo,
    Certification,
    Publicite,
)


# ─────────────────────────────────────────────
# USER
# ─────────────────────────────────────────────

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ['username', 'email', 'role', 'pays', 'is_active', 'date_joined']
    list_filter   = ['role', 'is_active']
    list_editable = ['role', 'is_active']
    search_fields = ['username', 'email']
    ordering      = ['-date_joined']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Informations supplémentaires', {
            'fields': ('role', 'pays', 'telephone', 'avatar')
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Informations supplémentaires', {
            'fields': ('email', 'role', 'pays', 'telephone', 'avatar')
        }),
    )

    def apercu_avatar(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="height:40px;width:40px;border-radius:50%;object-fit:cover;"/>',
                obj.avatar.url
            )
        return "—"
    apercu_avatar.short_description = "Avatar"


# ─────────────────────────────────────────────
# PROFIL UTILISATEUR
# ─────────────────────────────────────────────

@admin.register(ProfilUtilisateur)
class ProfilUtilisateurAdmin(admin.ModelAdmin):
    list_display  = ['utilisateur', 'bio_courte', 'date_naissance', 'total_votes', 'total_dl']
    search_fields = ['utilisateur__username', 'utilisateur__email']

    def total_votes(self, obj):
        return obj.total_votes_donnes()
    total_votes.short_description = "Votes donnés"

    def total_dl(self, obj):
        return obj.total_telechargements()
    total_dl.short_description = "Téléchargements"


# ─────────────────────────────────────────────
# PROFIL ARTISTE
# ─────────────────────────────────────────────

@admin.register(ProfilArtiste)
class ProfilArtisteAdmin(admin.ModelAdmin):
    list_display  = [
        'nom_artiste', 'utilisateur', 'genre', 'ville',
        'verified', 'apercu_photo', 'nb_morceaux',
        'nb_votes', 'nb_dl'
    ]
    list_filter   = ['genre', 'verified']
    list_editable = ['verified']
    search_fields = ['nom_artiste', 'utilisateur__username']
    readonly_fields = ['apercu_photo', 'apercu_cover', 'nb_morceaux', 'nb_votes', 'nb_dl']

    fieldsets = (
        ('Compte lié', {
            'fields': ('utilisateur',)
        }),
        ('Informations publiques', {
            'fields': ('nom_artiste', 'bio', 'genre', 'ville', 'verified')
        }),
        ('Médias', {
            'fields': ('photo', 'apercu_photo', 'photo_cover', 'apercu_cover')
        }),
        ('Réseaux sociaux', {
            'fields': ('facebook', 'instagram', 'twitter')
        }),
        ('Statistiques', {
            'fields': ('nb_morceaux', 'nb_votes', 'nb_dl')
        }),
    )

    def apercu_photo(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="height:60px;width:60px;border-radius:50%;object-fit:cover;"/>',
                obj.photo.url
            )
        return "—"
    apercu_photo.short_description = "Photo"

    def apercu_cover(self, obj):
        if obj.photo_cover:
            return format_html(
                '<img src="{}" style="height:60px;width:200px;object-fit:cover;border-radius:4px;"/>',
                obj.photo_cover.url
            )
        return "—"
    apercu_cover.short_description = "Cover"

    def nb_morceaux(self, obj):
        return obj.total_morceaux()
    nb_morceaux.short_description = "Morceaux validés"

    def nb_votes(self, obj):
        return obj.total_votes()
    nb_votes.short_description = "Votes reçus"

    def nb_dl(self, obj):
        return obj.total_telechargements()
    nb_dl.short_description = "Téléchargements"


# ─────────────────────────────────────────────
# PROFIL ADMINISTRATEUR
# ─────────────────────────────────────────────

@admin.register(ProfilAdministrateur)
class ProfilAdministrateurAdmin(admin.ModelAdmin):
    list_display  = ['utilisateur', 'niveau', 'service', 'cree_par']
    list_filter   = ['niveau']
    search_fields = ['utilisateur__username', 'service']

    fieldsets = (
        ('Compte lié', {
            'fields': ('utilisateur',)
        }),
        ('Informations admin', {
            'fields': ('niveau', 'service', 'cree_par')
        }),
    )


# ─────────────────────────────────────────────
# MORCEAU
# ─────────────────────────────────────────────

@admin.register(Morceau)
class MorceauAdmin(admin.ModelAdmin):
    list_display  = [
        'titre', 'artiste', 'genre', 'statut',
        'points', 'rang', 'apercu_pochette', 'lecteur_audio', 'date_sortie'
    ]
    list_filter   = ['statut', 'genre']
    list_editable = ['statut']
    search_fields = ['titre', 'artiste__nom_artiste']
    readonly_fields = ['points', 'rang', 'lecteur_audio', 'apercu_pochette', 'nb_tl', 'nb_vt']
    ordering      = ['-points']
    actions       = ['valider_morceaux', 'refuser_morceaux']

    fieldsets = (
        ('Informations', {
            'fields': ('artiste', 'titre', 'genre', 'date_sortie', 'statut')
        }),
        ('Fichiers', {
            'fields': ('pochette', 'apercu_pochette', 'fichier_mp3', 'lecteur_audio', 'duree')
        }),
        ('Classement', {
            'fields': ('points', 'rang')
        }),
        ('Statistiques', {
            'fields': ('nb_tl', 'nb_vt')
        }),
    )

    def apercu_pochette(self, obj):
        if obj.pochette:
            return format_html(
                '<img src="{}" style="height:50px;width:50px;object-fit:cover;border-radius:4px;"/>',
                obj.pochette.url
            )
        return "—"
    apercu_pochette.short_description = "Pochette"

    def lecteur_audio(self, obj):
        if obj.fichier_mp3:
            return format_html(
                '<audio controls style="height:30px;width:250px;">'
                '<source src="{}" type="audio/mpeg">'
                '</audio>',
                obj.fichier_mp3.url
            )
        return "—"
    lecteur_audio.short_description = "Écouter"

    def nb_tl(self, obj):
        return obj.nb_telechargements()
    nb_tl.short_description = "Téléchargements"

    def nb_vt(self, obj):
        return obj.nb_votes()
    nb_vt.short_description = "Votes"

    @admin.action(description="✅ Valider les morceaux sélectionnés")
    def valider_morceaux(self, request, queryset):
        nb = queryset.update(statut='valide')
        self.message_user(request, f"{nb} morceau(x) validé(s) avec succès.")

    @admin.action(description="❌ Refuser les morceaux sélectionnés")
    def refuser_morceaux(self, request, queryset):
        nb = queryset.update(statut='refuse')
        self.message_user(request, f"{nb} morceau(x) refusé(s).")


# ─────────────────────────────────────────────
# VIDÉO
# ─────────────────────────────────────────────

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display  = [
        'titre', 'artiste', 'morceau', 'statut',
        'nb_vues', 'apercu_thumbnail', 'apercu_video', 'created_at'
    ]
    list_filter   = ['statut']
    list_editable = ['statut']
    search_fields = ['titre', 'artiste__nom_artiste']
    readonly_fields = ['apercu_thumbnail', 'apercu_video', 'nb_vues']
    actions       = ['valider_videos', 'refuser_videos']

    fieldsets = (
        ('Informations', {
            'fields': ('artiste', 'morceau', 'titre', 'statut')
        }),
        ('Fichiers', {
            'fields': ('fichier_video', 'apercu_video', 'youtube_url', 'thumbnail', 'apercu_thumbnail')
        }),
        ('Statistiques', {
            'fields': ('nb_vues',)
        }),
    )

    def apercu_thumbnail(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="height:50px;width:90px;object-fit:cover;border-radius:4px;"/>',
                obj.thumbnail.url
            )
        return "—"
    apercu_thumbnail.short_description = "Thumbnail"

    def apercu_video(self, obj):
        if obj.fichier_video:
            return format_html(
                '<video controls style="height:80px;width:150px;border-radius:4px;">'
                '<source src="{}">'
                '</video>',
                obj.fichier_video.url
            )
        if obj.youtube_url:
            return format_html(
                '<a href="{}" target="_blank">'
                '<span style="background:#FF0000;color:white;padding:4px 8px;'
                'border-radius:4px;font-size:12px;">▶ YouTube</span></a>',
                obj.youtube_url
            )
        return "—"
    apercu_video.short_description = "Aperçu"

    @admin.action(description="✅ Valider les vidéos sélectionnées")
    def valider_videos(self, request, queryset):
        nb = queryset.update(statut='valide')
        self.message_user(request, f"{nb} vidéo(s) validée(s) avec succès.")

    @admin.action(description="❌ Refuser les vidéos sélectionnées")
    def refuser_videos(self, request, queryset):
        nb = queryset.update(statut='refuse')
        self.message_user(request, f"{nb} vidéo(s) refusée(s).")


# ─────────────────────────────────────────────
# TÉLÉCHARGEMENT
# ─────────────────────────────────────────────

@admin.register(Telechargement)
class TelechargementAdmin(admin.ModelAdmin):
    list_display  = ['morceau', 'user', 'ip_address', 'pub_vue', 'created_at']
    list_filter   = ['pub_vue']
    search_fields = ['morceau__titre', 'user__username', 'ip_address']
    readonly_fields = ['morceau', 'user', 'ip_address', 'pub_vue', 'created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# ─────────────────────────────────────────────
# VOTE
# ─────────────────────────────────────────────

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display  = ['morceau', 'user', 'created_at']
    search_fields = ['morceau__titre', 'user__username']
    readonly_fields = ['morceau', 'user', 'created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# ─────────────────────────────────────────────
# VUE VIDÉO
# ─────────────────────────────────────────────

@admin.register(VueVideo)
class VueVideoAdmin(admin.ModelAdmin):
    list_display  = ['video', 'user', 'session_id', 'created_at']
    search_fields = ['video__titre', 'user__username']
    readonly_fields = ['video', 'user', 'session_id', 'created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# ─────────────────────────────────────────────
# CERTIFICATION
# ─────────────────────────────────────────────

@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display  = ['morceau', 'niveau', 'valide_par', 'date']
    list_filter   = ['niveau']
    search_fields = ['morceau__titre']


# ─────────────────────────────────────────────
# PUBLICITÉ
# ─────────────────────────────────────────────

@admin.register(Publicite)
class PubliciteAdmin(admin.ModelAdmin):
    list_display  = [
        'annonceur', 'duree_secondes', 'actif',
        'nb_affichages', 'apercu_image', 'created_at'
    ]
    list_filter   = ['actif']
    list_editable = ['actif', 'duree_secondes']
    search_fields = ['annonceur']
    readonly_fields = ['nb_affichages', 'apercu_image']

    def apercu_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:60px;object-fit:cover;border-radius:4px;"/>',
                obj.image.url
            )
        return "—"
    apercu_image.short_description = "Aperçu"


# ─────────────────────────────────────────────
# TITRE DU SITE ADMIN
# ─────────────────────────────────────────────

admin.site.site_header = "🎵 Badju's Records — Administration"
admin.site.site_title  = "Badju's Records"
admin.site.index_title = "Tableau de bord"