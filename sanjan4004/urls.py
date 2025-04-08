"""
URL configuration for sanjan4004 project.

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
from django.urls import path,include
from WorldTtance.views import homepage
from WorldTtance import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('admin/', admin.site.urls),
    path('WorldTtance/', include('WorldTtance.urls')),
    path('payments/', include('payments.urls')),##mpesa payments etc
    path("WorldTtance/api/", include("WorldTtance.api.urls")),  # Include API URLs
    path('accounts/', include('allauth.urls')),


    

]

#LOADS THE USER PROFILE PICTURE IN THE BROWSER
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
