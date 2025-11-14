from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from tienda.views import logout_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('tienda.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', logout_view, name='logout'),
]
