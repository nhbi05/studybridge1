from django.urls import path
from .views import register_student, login_student,logout_student,get_current_user

urlpatterns = [
    path('register/', register_student, name='register'),
    path('login/', login_student, name='login'),
    path('logout/', logout_student, name='logout'),
    path('user', get_current_user, name='user'),
]
