from django.urls import path
from . import views

urlpatterns = [
    path('aleatoire/', views.pub_aleatoire, name='pub_aleatoire'),
]