from django.urls import path
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

from . import views

app_name = 'auctions'

urlpatterns = [
    path("", views.index.as_view(), name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("listing/<int:pk>", views.ListingView.as_view(), name="listing"),
    path("listing/<int:pk>/raise", views.raise_bid, name="raise_bid"),
    path("listing/<int:pk>/change_wishlist", views.change_wishlist, name="change_wishlist"),
    path("wishlist", login_required(views.WishlistView.as_view(), login_url=reverse_lazy("auctions:login")),
         name="wishlist"),
    path("close_listing/<int:pk>", views.close_listing, name="close_listing")
]
