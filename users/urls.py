from django.urls import path
from . import views

urlpatterns = [
    path('inscription/',     views.inscription,     name='inscription'),
    path('connexion/',       views.connexion,        name='connexion'),
    path('deconnexion/',     views.deconnexion,      name='deconnexion'),
    path('mon-espace/',      views.mon_espace,       name='mon_espace'),
    path('devenir-artiste/', views.devenir_artiste,  name='devenir_artiste'),
    path('modifier-profil/', views.modifier_profil,  name='modifier_profil'),
    path('profil/<str:username>/', views.profil_public, name='profil_public'),
    path('notifications/',           views.notifications,               name='notifications'),
    path('notifications/nb/',        views.nb_notifications_non_lues,   name='nb_notifications'),
    path('telechargements/', views.mes_telechargements, name='mes_telechargements'),
]