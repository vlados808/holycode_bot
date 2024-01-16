"""holycode URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

import sys
sys.path.append("..")

# from ..benchmark.views import process_msg
from benchmark import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('check/', views.check, name='check'),
    path('process/', views.process, name='process'),
    path('actualize/', views.actualize, name='actualize'),
    path('close/', views.close, name='close'),
    path('pause/', views.pause, name='pause'),
    path('check_tg_user/', views.check_tg_user, name='check_tg_user'),
    path('create_partner/', views.create_partner, name='create_partner'),
    path('resume/', views.resume, name='resume'),
    # path('tt17me_bot/', include(tt17me_bot_urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
