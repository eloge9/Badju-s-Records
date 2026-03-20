from django import forms
from models_app.models import Morceau, Video
import os


class MorceauForm(forms.ModelForm):
    class Meta:
        model  = Morceau
        fields = ['titre', 'genre', 'pochette', 'fichier_mp3', 'date_sortie']
        widgets = {
            'titre': forms.TextInput(attrs={
                'placeholder': 'Titre du morceau',
                'class': 'form-input'
            }),
            'genre': forms.Select(attrs={
                'class': 'upload-input'
            }),
            'date_sortie': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-input'
            }),
        }

    def clean_fichier_mp3(self):
        fichier = self.cleaned_data.get('fichier_mp3')
        if fichier and hasattr(fichier, 'name'):
            ext = os.path.splitext(fichier.name)[1].lower()
            if ext not in ['.mp3', '.wav', '.ogg']:
                raise forms.ValidationError("Seuls MP3, WAV et OGG sont autorisés.")
            if fichier.size > 100 * 1024 * 1024:
                raise forms.ValidationError("Le fichier ne doit pas dépasser 100 MB.")
        return fichier

    def clean_pochette(self):
        image = self.cleaned_data.get('pochette')
        if image and hasattr(image, 'name'):
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
                raise forms.ValidationError("Seuls JPG, PNG et WEBP sont autorisés.")
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("L'image ne doit pas dépasser 5 MB.")
        return image


class VideoForm(forms.ModelForm):

    def __init__(self, *args, artiste=None, **kwargs):
        super().__init__(*args, **kwargs)

        # ── Filtrer les morceaux par artiste ──
        if artiste:
            morceaux_artiste = Morceau.objects.filter(
                artiste=artiste,
                statut='valide'
            ).order_by('-created_at')

            self.fields['morceau'].queryset = morceaux_artiste

            # Message d'aide selon le nombre de morceaux disponibles
            if morceaux_artiste.exists():
                self.fields['morceau'].help_text = (
                    f"{morceaux_artiste.count()} morceau(x) disponible(s). "
                    "Lier la vidéo à un morceau permet d'augmenter ses points."
                )
            else:
                self.fields['morceau'].help_text = (
                    "Aucun morceau validé disponible. "
                    "Ajoutez d'abord un morceau et attendez sa validation."
                )
        else:
            self.fields['morceau'].queryset = Morceau.objects.none()

        # Morceau optionnel
        self.fields['morceau'].required  = False
        self.fields['morceau'].empty_label = "-- Aucun morceau lié (optionnel) --"

    class Meta:
        model  = Video
        fields = ['titre', 'morceau', 'description', 'fichier_video', 'youtube_url', 'thumbnail']
        widgets = {
            'titre': forms.TextInput(attrs={
                'placeholder': 'Titre de la vidéo',
                'class': 'form-input'
            }),
            'morceau': forms.Select(attrs={
                'class': 'form-input'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Décris ta vidéo, les paroles, le contexte...',
                'class': 'form-input',
                'rows': 3
            }),
            'youtube_url': forms.URLInput(attrs={
                'placeholder': 'https://youtube.com/watch?v=...',
                'class': 'form-input'
            }),
        }
        labels = {
            'morceau':      'Morceau lié (optionnel)',
            'fichier_video': 'Fichier vidéo (MP4, WEBM, MOV)',
            'youtube_url':   'Ou lien YouTube',
            'thumbnail':     'Miniature (image de couverture)',
        }

    def clean(self):
        cleaned = super().clean()
        fichier = cleaned.get('fichier_video')
        youtube = cleaned.get('youtube_url')
        if not fichier and not youtube:
            raise forms.ValidationError(
                "Fournissez un fichier vidéo (MP4) ou un lien YouTube."
            )
        return cleaned

    def clean_fichier_video(self):
        fichier = self.cleaned_data.get('fichier_video')
        if fichier and hasattr(fichier, 'name'):
            ext = os.path.splitext(fichier.name)[1].lower()
            if ext not in ['.mp4', '.webm', '.mov']:
                raise forms.ValidationError("Seuls MP4, WEBM et MOV sont autorisés.")
            if fichier.size > 500 * 1024 * 1024:
                raise forms.ValidationError("La vidéo ne doit pas dépasser 500 MB.")
        return fichier

    def clean_thumbnail(self):
        thumbnail = self.cleaned_data.get('thumbnail')
        if thumbnail and hasattr(thumbnail, 'name'):
            ext = os.path.splitext(thumbnail.name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
                raise forms.ValidationError("Seuls JPG, PNG et WEBP sont autorisés.")
            if thumbnail.size > 5 * 1024 * 1024:
                raise forms.ValidationError("La miniature ne doit pas dépasser 5 MB.")
        return thumbnail