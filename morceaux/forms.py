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
                'class': 'form-input'
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
        # Filtrer les morceaux pour n'afficher que ceux de cet artiste
        if artiste:
            self.fields['morceau'].queryset = Morceau.objects.filter(
                artiste=artiste,
                statut='valide'
            )
        self.fields['morceau'].required = False

    class Meta:
        model  = Video
        fields = ['titre', 'morceau', 'fichier_video', 'youtube_url', 'thumbnail']
        widgets = {
            'titre': forms.TextInput(attrs={
                'placeholder': 'Titre de la vidéo',
                'class': 'form-input'
            }),
            'morceau': forms.Select(attrs={
                'class': 'form-input'
            }),
            'youtube_url': forms.URLInput(attrs={
                'placeholder': 'https://youtube.com/watch?v=...',
                'class': 'form-input'
            }),
        }

    def clean(self):
        cleaned  = super().clean()
        fichier  = cleaned.get('fichier_video')
        youtube  = cleaned.get('youtube_url')
        if not fichier and not youtube:
            raise forms.ValidationError("Fournissez un fichier vidéo ou un lien YouTube.")
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