from django.urls import path
from . import views

urlpatterns = [
    path('',                     views.accueil,            name='accueil'),
    path('top100/',              views.top100,             name='top100'),
    path('morceau/<int:id>/',    views.detail_morceau,     name='detail_morceau'),
    path('tv/',                  views.badju_tv,           name='badju_tv'),
    path('video/<int:id>/',      views.detail_video,       name='detail_video'),
    path('recherche/',           views.recherche_globale,   name='recherche'),
    path('dashboard/',           views.dashboard_artiste,   name='dashboard'),
    path('ajouter/morceau/',     views.ajouter_morceau,     name='ajouter_morceau'),
    path('modifier/morceau/<int:id>/', views.modifier_morceau, name='modifier_morceau'),
    path('supprimer/morceau/<int:id>/', views.supprimer_morceau, name='supprimer_morceau'),
    path('ajouter/video/',       views.ajouter_video,       name='ajouter_video'),
    path('modifier/video/<int:id>/',   views.modifier_video,   name='modifier_video'),
    path('supprimer/video/<int:id>/',   views.supprimer_video,   name='supprimer_video'),
]