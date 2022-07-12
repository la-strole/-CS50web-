from django.urls import path
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

from . import views

app_name = 'auctions'

urlpatterns = [
    path("", views.index.as_view(), name="index"),
    path("index", views.index.as_view(), name='index_new'),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("listing/<int:pk>", login_required(views.ListingView.as_view(), login_url=reverse_lazy("auctions:login")),
         name="listing"),
    path("<path:url>/raise/<int:pk>", views.raise_bid, name="raise_bid"),
    path("<path:url>/change_wishlist/<int:pk>", views.change_wishlist, name="change_wishlist"),
    path("wishlist", views.wishlist_view, name="wishlist"),
    path("<path:url>/close_listing/<int:pk>", views.close_listing, name="close_listing"),
    path("add_comment/<int:pk>", views.add_comment, name="add_comment"),
    path("categories", views.Categories.as_view(), name="categories"),
    path("notifications/read/<int:pk>", views.mark_notification_read, name="mark_as_read"),
    path("notifications", login_required(views.NotificationsView.as_view(), login_url=reverse_lazy("auctions:login")),
         name='notifications'),

]
