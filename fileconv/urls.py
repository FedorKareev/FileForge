from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('convert/', include('converter.urls')),
    path('qr/', include('qrscan.urls')),
    path('ocr/', include('ocr.urls')),
]