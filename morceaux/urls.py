from django.urls import path
from . import views

urlpatterns = [
    path('',                                    views.accueil,           name='accueil'),
    path('top100/',                             views.top100,            name='top100'),
    path('morceau/<int:id>/',                   views.detail_morceau,    name='detail_morceau'),
    path('video/<int:id>/',                     views.detail_video,      name='detail_video'),
    path('tv/',                                 views.badju_tv,          name='badju_tv'),
    path('dashboard/',                          views.dashboard_artiste, name='dashboard'),
    path('dashboard/ajouter-morceau/',          views.ajouter_morceau,   name='ajouter_morceau'),
    path('dashboard/ajouter-video/',            views.ajouter_video,     name='ajouter_video'),
    path('dashboard/modifier-morceau/<int:id>/',views.modifier_morceau,  name='modifier_morceau'),
    path('dashboard/supprimer-morceau/<int:id>/',views.supprimer_morceau,name='supprimer_morceau'),
]