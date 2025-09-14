from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('session/<int:session_id>/', views.chat_view, name='chat_session'),
    path('api/send/<int:session_id>/', views.send_message, name='send_message'),
    path('new/', views.new_chat, name='new_chat'),
    path('delete/<int:session_id>/', views.delete_chat, name='delete_chat'),
    path('api/login/google/', views.google_login, name='google_login'),
    path('auth/callback/', views.google_callback, name='google_callback'),
    path('logout/', views.logout_view, name='logout'),
]