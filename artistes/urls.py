from django.urls import path
from . import views

urlpatterns = [
    path('',         views.liste_artistes, name='liste_artistes'),
    path('<int:id>/', views.detail_artiste, name='detail_artiste'),
]