from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('registration/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('home/', views.home, name='home'),
    path('about_us/', views.about_us, name='about_us'),
    path('contact/', views.contact, name='contact'),
    path('learn/', views.learn, name='learn'),
    path('teach/', views.teach, name='teach'),
    path('profile/', views.view_profile, name='profile'),
    path('profile/<str:username>/',views.view_other_user_profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('follow/', views.follow_user, name='follow_user'),
    path('skill-requests/', views.skill_requests, name='skill_requests'),
    path('session_schedule/', views.session_schedule, name='session_schedule'),
    path('schedule-session/<int:request_id>/', views.schedule_session, name='schedule_session'),
    path('send-skill-request/<int:receiver_id>/', views.send_skill_request, name='send_skill_request'),
    # path('session_schedule/<int:request_id>/', views.session_schedule, name='session_schedule'),
    path('accept-skill-request/<int:request_id>/', views.accept_skill_request, name='accept_skill_request'),
    path('reject-skill-request/<int:request_id>/', views.reject_skill_request, name='reject_skill_request'),
    path('sent-skill-requests/', views.sent_skill_requests, name='sent_skill_requests'),
    path('manage-session/<int:session_id>/', views.manage_session, name='manage_session'),
     path('create_review/<int:session_id>/', views.create_review, name='create_review'),
#     path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),
    path('admin_index/', views.admin_index, name='admin_index'),
    path('activate_user/<int:user_id>/', views.activate_user, name='activate_user'),
    path('deactivate_user/<int:user_id>/', views.deactivate_user, name='deactivate_user'),
    path('add_skills/', views.add_skill, name='add_skill'),
    path('search/', views.search_users, name='search_users'),
    path('password_reset/', auth_views.PasswordResetView.as_view(),name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('accounts/login/', views.user_login, name='login'),
]
