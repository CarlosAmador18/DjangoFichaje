"""
URL configuration for ficharDjango project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from fichar import views as fichar_views
from django.contrib.auth.views import LogoutView



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', fichar_views.login_view, name='index'),
    path('login/', fichar_views.login_view, name='login'),
    path('logoutf/', fichar_views.logout_view, name='logoutf'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('conexion/', fichar_views.obtener_conexion, name='conexion'),
    path('fichar/', fichar_views.fichar, name='fichar'),
    path('map/', fichar_views.map, name='map'),
    path('horario/', fichar_views.horario, name='horario'),
    path('registrar/', fichar_views.registro, name='registrar'),
    path('registro/', fichar_views.irregistros, name='registro'),
    path('obtener/', fichar_views.obtener_registros, name='obtener'),
    path('obtenerhorarios/', fichar_views.obtenerhorarios, name='obtenerhorarios'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
