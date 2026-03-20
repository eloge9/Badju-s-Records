from django.urls import path
from . import views

urlpatterns = [
    path('recalculer/', views.recalculer, name='recalculer_classement'),
]