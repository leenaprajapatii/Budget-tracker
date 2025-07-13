from django.urls import path
from . import views
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('transactions/', views.transactions, name='transactions'),
    path('add-transaction/', views.add_transaction, name='add_transaction'),
    path('delete-transaction/<int:pk>/', views.delete_transaction, name='delete_transaction'),
    path('profile/', views.profile, name='profile'),
    path('goals/', views.goals, name='goals'),
    path('add-goal/', views.goals, name='add_goal'),
    path('update-goal/<int:pk>/', views.update_goal, name='update_goal'),
    path('delete-goal/<int:pk>/', views.delete_goal, name='delete_goal'),
    path('add-category/', views.add_category, name='add_category'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='tracker/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('set-password/', views.set_password, name='set_password'),
]