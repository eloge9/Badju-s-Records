from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from models_app.models import User, ProfilUtilisateur, ProfilArtiste
import os


# ─────────────────────────────────────────────
# INSCRIPTION
# ─────────────────────────────────────────────

class InscriptionForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Mot de passe',
            'class': 'form-input'
        })
    )
    password2 = forms.CharField(
        label='Confirmer le mot de passe',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirmer le mot de passe',
            'class': 'form-input'
        })
    )

    class Meta:
        model  = User
        fields = ['username', 'email', 'pays', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': "Nom d'utilisateur",
                'class': 'form-input'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Adresse email',
                'class': 'form-input'
            }),
            'pays': forms.TextInput(attrs={
                'placeholder': 'Votre pays',
                'class': 'form-input'
            }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Un compte avec cet email existe déjà.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError("Ce nom d'utilisateur est déjà pris.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password1    = cleaned_data.get('password1')
        password2    = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data

    def save(self, commit=True):
        user          = super().save(commit=False)
        user.role     = 'utilisateur'
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            # Créer automatiquement le ProfilUtilisateur lié
            ProfilUtilisateur.objects.create(utilisateur=user)
        return user


# ─────────────────────────────────────────────
# CONNEXION
# ─────────────────────────────────────────────

class ConnexionForm(AuthenticationForm):
    username = forms.CharField(
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={
            'placeholder': "Nom d'utilisateur",
            'class': 'form-input'
        })
    )
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Mot de passe',
            'class': 'form-input'
        })
    )


# ─────────────────────────────────────────────
# MODIFIER PROFIL UTILISATEUR
# ─────────────────────────────────────────────

class ModifierProfilForm(forms.ModelForm):
    class Meta:
        model  = User
        fields = ['first_name', 'last_name', 'email', 'pays', 'telephone', 'avatar']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'Prénom',
                'class': 'form-input'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Nom',
                'class': 'form-input'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Email',
                'class': 'form-input'
            }),
            'pays': forms.TextInput(attrs={
                'placeholder': 'Pays',
                'class': 'form-input'
            }),
            'telephone': forms.TextInput(attrs={
                'placeholder': 'Téléphone',
                'class': 'form-input'
            }),
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar and hasattr(avatar, 'name'):
            ext = os.path.splitext(avatar.name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
                raise ValidationError("Format non autorisé. Utilisez jpg, png ou webp.")
            if avatar.size > 5 * 1024 * 1024:
                raise ValidationError("L'image ne doit pas dépasser 5 MB.")
        return avatar


# ─────────────────────────────────────────────
# CRÉER PROFIL ARTISTE
# (un utilisateur qui veut devenir artiste)
# ─────────────────────────────────────────────

class CreerProfilArtisteForm(forms.ModelForm):
    class Meta:
        model  = ProfilArtiste
        fields = [
            'nom_artiste', 'bio', 'genre', 'ville',
            'photo', 'photo_cover',
            'facebook', 'instagram', 'twitter'
        ]
        widgets = {
            'nom_artiste': forms.TextInput(attrs={
                'placeholder': 'Votre nom de scène',
                'class': 'form-input'
            }),
            'bio': forms.Textarea(attrs={
                'placeholder': 'Parlez de vous...',
                'class': 'form-input',
                'rows': 4
            }),
            'genre': forms.Select(attrs={
                'class': 'form-input'
            }),
            'ville': forms.TextInput(attrs={
                'placeholder': 'Votre ville',
                'class': 'form-input'
            }),
            'facebook': forms.URLInput(attrs={
                'placeholder': 'https://facebook.com/...',
                'class': 'form-input'
            }),
            'instagram': forms.URLInput(attrs={
                'placeholder': 'https://instagram.com/...',
                'class': 'form-input'
            }),
            'twitter': forms.URLInput(attrs={
                'placeholder': 'https://twitter.com/...',
                'class': 'form-input'
            }),
        }

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo and hasattr(photo, 'name'):
            ext = os.path.splitext(photo.name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
                raise ValidationError("Format non autorisé. Utilisez jpg, png ou webp.")
            if photo.size > 5 * 1024 * 1024:
                raise ValidationError("La photo ne doit pas dépasser 5 MB.")
        return photo

    def clean_photo_cover(self):
        cover = self.cleaned_data.get('photo_cover')
        if cover and hasattr(cover, 'name'):
            ext = os.path.splitext(cover.name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.webp']:
                raise ValidationError("Format non autorisé. Utilisez jpg, png ou webp.")
            if cover.size > 5 * 1024 * 1024:
                raise ValidationError("La cover ne doit pas dépasser 5 MB.")
        return cover