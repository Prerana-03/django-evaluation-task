from django.urls import path
from . import views

urlpatterns = [
    # Public views
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    
    # User views
    path('user/dashboard/', views.user_dashboard, name='user_dashboard'),
    path('user/profile/', views.user_profile, name='user_profile'),
    path('user/task/<int:app_id>/', views.task_detail, name='task_detail'),
    
    # Admin views
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/apps/', views.admin_app_list, name='admin_app_list'),
    path('admin-dashboard/apps/add/', views.admin_app_form, name='admin_app_add'),
    path('admin-dashboard/apps/edit/<int:app_id>/', views.admin_app_form, name='admin_app_edit'),
]
