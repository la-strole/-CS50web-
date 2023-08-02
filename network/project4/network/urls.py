
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("api/newPost", views.api_new_post, name="api_new_post"),
    path("userProfile", views.user_profile, name="user_profile"),
    path("api/follow", views.api_follow, name="api_follow"),
    path("followedUsers", views.followed_users, name="followed_users"),
    path("api/editpost", views.api_edit_post, name="api_edit_post"),
    path("api/likebutton", views.api_like_button, name="api_likebutton"),
    path("api/dislikebutton", views.api_dislike_button, name="api_dislikebutton"),
]
