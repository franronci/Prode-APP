from django.urls import path
from django.contrib.auth import views as auth_views # Importamos vistas de autenticación
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    # --- RUTAS DE ACCESO ---
    path('registro/', views.registro, name='registro'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # --- RUTAS DEL JUEGO ---
    path('prode/', views.prode, name='prode'),
    path('ranking/', views.ranking, name='ranking'),
    
    # --- RUTAS DE TORNEOS ---
    path('torneos/', views.mis_torneos, name='mis_torneos'),
    path('torneos/<int:torneo_id>/', views.detalle_torneo, name='detalle_torneo'),
]