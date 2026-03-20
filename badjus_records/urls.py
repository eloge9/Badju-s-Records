from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/',      admin.site.urls),
    path('',            include('morceaux.urls')),
    path('artistes/',   include('artistes.urls')),
    path('engagement/', include('engagement.urls')),
    path('classement/', include('classement.urls')),
    path('',            include('users.urls')),
    path('publicites/', include('publicites.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Pages d'erreur custom
handler404 = 'morceaux.views.page_404'
handler500 = 'morceaux.views.page_500'