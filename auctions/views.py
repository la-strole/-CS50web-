import logging
import os

from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from .models import User, Listing
from auctions import forms

# Add logger
logger_views = logging.getLogger('views')
f_handler = logging.FileHandler('general.log')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
f_handler.setFormatter(f_format)
logger_views.addHandler(f_handler)
logger_views.setLevel(os.getenv('DJANGO_LOG_LEVEL'))


def index(request):
    return render(request, "auctions/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")


@login_required(login_url=reverse_lazy("auctions:login"))
def create_listing(request):
    if request.method == "POST":
        populated_form = forms.CreateListing(request.POST)
        if populated_form.is_valid():
            data = populated_form.cleaned_data
            logger_views.debug(f"Try to add  new listing ({data.get('title')}) to database for user {request.user}.")
            data.update({'user': request.user})
            result = Listing.create_listing(data)
            if result:
                success_msg = f"Create new listing: {result.title}."
                return HttpResponseRedirect(reverse("auctions:listing", kwargs={'listing_id': result.id}))
            else:
                error_msg = 'Can not add this listing, please try again.'
                return HttpResponseRedirect(reverse("auctions:create_listing"))

    elif request.method == "GET":
        form = forms.CreateListing()
        return render(request, 'auctions/create_listing.html', {'form': form})


def listing_view(request, listing_id: int):
    """
    Return listing view for listing_id
    :type listing_id: int
    """
    if request.method == "GET":
        try:
            listing_id = int(listing_id)
            assert listing_id > 0
        except (ValueError, AssertionError) as e:
            logger_views.debug(f"Listing_id in request is not integer. it is ({listing_id})")

        listing = get_object_or_404(Listing, pk=listing_id)
        if listing.active:
            current_bid = Listing.get_current_bid(listing)
            return render(request, "auctions/listing.html", {"data": listing,
                                                             "current_bid": current_bid
                                                             })
        else:
            msg = "Listing is not active."
            raise Http404(msg)
    elif request.method == "POST":

        try:
            listing = Listing.objects.get(id=listing_id)
            assert listing
            assert listing.active

            bid = request.POST.get('bid', None)
            wishlist_id = request.POST.get('wishlist', None)

            # Raise bid
            if bid:
                assert int(bid) > int(Listing.get_current_bid(listing))
                data = {'listing': listing,
                        'user': request.user,
                        'bid': bid
                        }
                result = Listing.raise_bid(data)
                assert result

            # Add/Delete from wishlist
            elif wishlist_id:


        except (TypeError, ValueError, AssertionError) as e:
            logger_views.error(f"Can not work with listing. {e}.")
            msg = "Can not work with listing."
            raise Http404(msg)
        return HttpResponseRedirect(reverse("auctions:listing", kwargs={'listing_id': listing_id}))
    else:
        raise Http404("Can not get page.")
