from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display, action
from django.utils.html import format_html
from .models import (
    User, ProfilUtilisateur, ProfilArtiste,
    Morceau, Video, Vote, Telechargement,
    Abonnement, Publicite
)


# ─────────────────────────────────────────────
# USER
# ─────────────────────────────────────────────

@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display  = ['username', 'email', 'role', 'pays', 'is_active', 'date_joined']
    list_filter   = ['role', 'is_active']
    search_fields = ['username', 'email']
    list_editable = ['role', 'is_active']
    compressed_fields = True


# ─────────────────────────────────────────────
# PROFIL UTILISATEUR
# ─────────────────────────────────────────────

@admin.register(ProfilUtilisateur)
class ProfilUtilisateurAdmin(ModelAdmin):
    list_display  = ['utilisateur', 'bio_courte', 'date_naissance', 'total_votes', 'total_dl']
    search_fields = ['utilisateur__username', 'utilisateur__email']
    compressed_fields = True

    @display(description="Votes donnés")
    def total_votes(self, obj):
        return obj.total_votes_donnes()

    @display(description="Téléchargements")
    def total_dl(self, obj):
        return obj.total_telechargements()


# ─────────────────────────────────────────────
# PROFIL ARTISTE
# ─────────────────────────────────────────────

@admin.register(ProfilArtiste)
class ProfilArtisteAdmin(ModelAdmin):
    list_display  = ['nom_artiste', 'genre', 'ville', 'verified', 'apercu_photo']
    list_filter   = ['genre', 'verified']
    list_editable = ['verified']
    search_fields = ['nom_artiste']
    compressed_fields = True

    @display(description="Photo", ordering="nom_artiste")
    def apercu_photo(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="height:40px;width:40px;'
                'border-radius:50%;object-fit:cover;"/>',
                obj.photo.url
            )
        return "—"


# ─────────────────────────────────────────────
# MORCEAU
# ─────────────────────────────────────────────

@admin.register(Morceau)
class MorceauAdmin(ModelAdmin):
    list_display    = ['titre', 'artiste', 'genre', 'statut_badge',
                       'points', 'rang', 'apercu_pochette', 'lecteur_audio']
    list_filter     = ['statut', 'genre']
    search_fields   = ['titre', 'artiste__nom_artiste']
    readonly_fields = ['points', 'rang', 'lecteur_audio', 'apercu_pochette']
    actions         = ['valider_morceaux', 'refuser_morceaux']
    compressed_fields = True

    @display(description="Statut", label={
        'valide':     'success',
        'en_attente': 'warning',
        'refuse':     'danger',
    })
    def statut_badge(self, obj):
        labels = {
            'valide':     '✅ Validé',
            'en_attente': '⏳ En attente',
            'refuse':     '❌ Refusé',
        }
        return obj.statut, labels.get(obj.statut, obj.statut)

    @display(description="Pochette")
    def apercu_pochette(self, obj):
        if obj.pochette:
            return format_html(
                '<img src="{}" style="height:48px;width:48px;'
                'border-radius:8px;object-fit:cover;"/>',
                obj.pochette.url
            )
        return "—"

    @display(description="Écouter")
    def lecteur_audio(self, obj):
        if obj.fichier_mp3:
            return format_html(
                '<audio controls style="height:32px;max-width:200px;">'
                '<source src="{}"></audio>',
                obj.fichier_mp3.url
            )
        return "—"

    @action(description="✅ Valider les morceaux sélectionnés")
    def valider_morceaux(self, request, queryset):
        queryset.update(statut='valide')
        self.message_user(request, f"{queryset.count()} morceau(x) validé(s).")

    @action(description="❌ Refuser les morceaux sélectionnés")
    def refuser_morceaux(self, request, queryset):
        queryset.update(statut='refuse')
        self.message_user(request, f"{queryset.count()} morceau(x) refusé(s).")


# ─────────────────────────────────────────────
# VIDÉO
# ─────────────────────────────────────────────

@admin.register(Video)
class VideoAdmin(ModelAdmin):
    list_display    = ['titre', 'artiste', 'statut_badge', 'nb_vues', 'apercu_video']
    list_filter     = ['statut']
    search_fields   = ['titre', 'artiste__nom_artiste']
    readonly_fields = ['nb_vues', 'apercu_video']
    actions         = ['valider_videos', 'refuser_videos']
    compressed_fields = True

    @display(description="Statut", label={
        'valide':     'success',
        'en_attente': 'warning',
        'refuse':     'danger',
    })
    def statut_badge(self, obj):
        labels = {
            'valide':     '✅ Validé',
            'en_attente': '⏳ En attente',
            'refuse':     '❌ Refusé',
        }
        return obj.statut, labels.get(obj.statut, obj.statut)

    @display(description="Aperçu")
    def apercu_video(self, obj):
        if obj.fichier_video:
            return format_html(
                '<video controls style="height:60px;max-width:180px;">'
                '<source src="{}"></video>',
                obj.fichier_video.url
            )
        if obj.youtube_url:
            return format_html(
                '<a href="{}" target="_blank" style="color:#F5A623;">▶ YouTube ↗</a>',
                obj.youtube_url
            )
        return "—"

    @action(description="✅ Valider les vidéos sélectionnées")
    def valider_videos(self, request, queryset):
        queryset.update(statut='valide')
        self.message_user(request, f"{queryset.count()} vidéo(s) validée(s).")

    @action(description="❌ Refuser les vidéos sélectionnées")
    def refuser_videos(self, request, queryset):
        queryset.update(statut='refuse')
        self.message_user(request, f"{queryset.count()} vidéo(s) refusée(s).")


# ─────────────────────────────────────────────
# PUBLICITÉ
# ─────────────────────────────────────────────

@admin.register(Publicite)
class PubliciteAdmin(ModelAdmin):
    list_display    = ['annonceur', 'duree_secondes', 'actif',
                       'nb_affichages', 'apercu_image']
    list_editable   = ['actif', 'duree_secondes']
    compressed_fields = True

    @display(description="Aperçu")
    def apercu_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:40px;border-radius:6px;"/>',
                obj.image.url
            )
        return "—"


# ─────────────────────────────────────────────
# VOTE, TÉLÉCHARGEMENT, ABONNEMENT
# ─────────────────────────────────────────────

@admin.register(Vote)
class VoteAdmin(ModelAdmin):
    list_display  = ['user', 'morceau', 'created_at']
    list_filter   = ['created_at']
    search_fields = ['user__username', 'morceau__titre']
    compressed_fields = True

@admin.register(Telechargement)
class TelechargementAdmin(ModelAdmin):
    list_display  = ['morceau', 'user', 'pub_vue', 'ip_address', 'created_at']
    list_filter   = ['pub_vue', 'created_at']
    search_fields = ['morceau__titre', 'user__username']
    compressed_fields = True

@admin.register(Abonnement)
class AbonnementAdmin(ModelAdmin):
    list_display  = ['abonne', 'artiste', 'created_at']
    search_fields = ['abonne__username', 'artiste__nom_artiste']
    compressed_fields = True