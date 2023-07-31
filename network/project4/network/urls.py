
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("api/newPost", views.api_new_post, name="api_new_post"),
    path("userProfile", views.user_profile, name="user_profile"),
]
