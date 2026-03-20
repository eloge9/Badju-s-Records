from django.urls import path
from . import views

urlpatterns = [
    path('voter/<int:morceau_id>/',       views.voter,                  name='voter'),
    path('telecharger/<int:morceau_id>/', views.valider_telechargement, name='telecharger'),
    path('vue-video/<int:video_id>/',     views.enregistrer_vue,        name='vue_video'),
]