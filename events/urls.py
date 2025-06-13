from django.urls import path
from . import views

urlpatterns = [
    # Public views
    path('', views.home, name='home'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),
    path('event/<int:event_id>/register/', views.register_event, name='register_event'),
    path('event/<int:event_id>/withdraw/', views.withdraw_registration, name='withdraw_registration'),
    path('search/', views.search_events, name='search_events'),
      # Team management
    path('event/<int:event_id>/team-choice/', views.team_choice, name='team_choice'),
    path('event/<int:event_id>/create-team/', views.create_team, name='create_team'),
    path('event/<int:event_id>/join-team/', views.join_team, name='join_team'),
    path('team/<int:team_id>/', views.manage_team, name='manage_team'),
    path('team/member/<int:member_id>/remove/', views.remove_team_member, name='remove_team_member'),
    path('team/<int:team_id>/delete/', views.delete_team, name='delete_team'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),
    path('student-login/', views.login_view, name='student_login'),
    path('admin-login/', views.login_view, name='admin_login'),
    
    # Student views
    path('my-registrations/', views.my_registrations, name='my_registrations'),
    
    # Admin views
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('create-event/', views.create_event, name='create_event'),
    path('edit-event/<int:event_id>/', views.edit_event, name='edit_event'),
    path('delete-event/<int:event_id>/', views.delete_event, name='delete_event'),
]
