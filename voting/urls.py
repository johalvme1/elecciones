from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'voting'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('votar/', views.ballot_view, name='ballot'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/add-party/', views.add_party_view, name='add_party'),
    path('dashboard/add-candidate/', views.add_candidate_view, name='add_candidate'),
    path('api/vote-count/', views.vote_count_api, name='vote_count_api'),
    path('resultados/', views.resultados_login, name='resultados_login'),
    path('resultados/logout/', views.resultados_logout, name='resultados_logout'),
    path('login/', auth_views.LoginView.as_view(template_name='voting/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
