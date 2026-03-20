from django.urls import path
from . import views

urlpatterns = [
    path('voter/<int:morceau_id>/',        views.voter,                  name='voter'),
    path('telecharger/<int:morceau_id>/',  views.valider_telechargement, name='telecharger'),
    path('vue-video/<int:video_id>/',      views.enregistrer_vue,        name='vue_video'),
    path('liker/<int:video_id>/',          views.liker_video,            name='liker_video'),
    path('commenter/<int:video_id>/',      views.commenter_video,        name='commenter_video'),
    path('get-pub-telechargement/',        views.get_pub_telechargement, name='get_pub_telechargement'),
]