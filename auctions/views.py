import logging
import os

from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import generic

from .models import User, Listing, Wishlist, Category
from auctions import forms

# Add logger
logger_views = logging.getLogger('views')
f_handler = logging.FileHandler('general.log')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
f_handler.setFormatter(f_format)
logger_views.addHandler(f_handler)
logger_views.setLevel(os.getenv('DJANGO_LOG_LEVEL'))


class Dataset:
    def __init__(self, listing: Listing, extra_data: dict):
        self.listing = listing
        self.ret_url = extra_data['ret_url']
        self.ret_close_url = extra_data['ret_close_url']
        self.exist_in_wishlist = extra_data['exist_in_wishlist']


class index(generic.ListView):
    model = Listing
    context_object_name = 'listings'
    template_name = 'auctions/index.html'

    def get_queryset(self):
        # Use for category filter
        category_name = self.request.GET.get('f', '')
        if category_name:
            listings = Listing.objects.filter(active=True, category__name=category_name)
            return listings
        else:
            listings = Listing.objects.filter(active=True)
        return listings

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(index, self).get_context_data(**kwargs)
        categories = Category.objects.all()
        context['categories'] = categories
        context['category_bage'] = self.request.GET.get('f', '')
        if self.request.user.is_active:
            context['wishlist_bage'] = len(Wishlist.objects.filter(user=self.request.user, listing__active=True))
        else:
            context['wishlist_bage'] = ''
        return context


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            msg = f"You had successfully login as {user}."
            messages.success(request, msg)
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            msg = f"Invalid username {username} and/or password."
            logger_views.warning(msg)
            messages.error(request, msg)
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    msg = "You successfully logout"
    messages.success(request, msg)
    return HttpResponseRedirect(reverse("auctions:index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            msg = f"Passwords for user {username} not match."
            logger_views.warning(msg)
            messages.error(request, msg)
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            msg = f"Error. Username {username} already taken."
            logger_views.warning(msg)
            messages.error(request, msg)
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        msg = f"You are succesfully login as {username}"
        messages.success(request, msg)
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")


@login_required(login_url=reverse_lazy("auctions:login"))
def create_listing(request):
    if request.method == "POST":
        populated_form = forms.CreateListing(request.POST)
        if populated_form.is_valid():
            data = populated_form.cleaned_data
            data['title'] = data['title'].lower().capitalize()
            logger_views.debug(f"Try to add  new listing ({data.get('title')}) to database for user {request.user}.")
            data.update({'user': request.user})
            result = Listing.create_listing(data)
            if result:
                msg = f"Create new listing: {result.title}."
                logger_views.warning(msg)
                messages.success(request, msg)
                return HttpResponseRedirect(reverse_lazy("auctions:listing", kwargs={'pk': result.id}))
            else:
                msg = 'Can not add this listing, please try again.'
                logger_views.error(msg)
                messages.error(request, msg)
                return HttpResponseRedirect(reverse("auctions:create_listing"))
        else:
            msg = f"Can not create listing. Form in invalid."
            logger_views.warning(msg)
            messages.error(request, msg)
            return HttpResponseRedirect(reverse("auctions:create_listing"))
    elif request.method == "GET":
        form = forms.CreateListing()
        return render(request, 'auctions/create_listing.html', {'form': form, 'categories': None})


class ListingView(generic.DetailView):
    """
    Return listing view for listing_id
    """

    model = Listing
    template_name = 'auctions/listing.html'
    context_object_name = 'listing'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(ListingView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        user = self.request.user
        ret_url = reverse('auctions:listing', kwargs={'pk': self.object.id})
        ret_close_url = reverse('auctions:index')
        extra_data = {'ret_url': ret_url,
                      'ret_close_url': ret_close_url,
                      'exist_in_wishlist': Wishlist.exist_in_wishlist(self.object, user)
                      }
        context['listing'] = [Dataset(self.object, extra_data)]

        if self.request.user.is_active:
            context['wishlist_bage'] = len(Wishlist.objects.filter(user=self.request.user))
        else:
            context['wishlist_bage'] = ''
        return context

    def get_queryset(self):
        result = Listing.objects.filter(active=True)
        return result


@login_required(login_url=reverse_lazy("auctions:login"))
def raise_bid(request, pk):
    if request.method == "POST":
        ret_url = request.POST.get('ret_url', '')
        listing = get_object_or_404(Listing, pk=pk)
        populated_form = forms.RaiseBid(request.POST)
        if populated_form.is_valid() and listing.active and ret_url:
            data = populated_form.cleaned_data
            current_bid = listing.get_current_bid.value
            try:
                assert int(data['value']) > int(current_bid)
                data.update({'user': request.user, 'listing': listing})
                result = Listing.raise_bid(data)
                if not result:
                    msg = f"Can not raise bid user:{request.user}, listing: {listing}, bid: {data['value']}"
                    logger_views.error(msg)
                    messages.error(request, msg)
                    return HttpResponseRedirect(ret_url)
                else:
                    msg = f"Successfully raise bid for {listing} to {data['value']} $"
                    messages.success(request, msg)
                    return HttpResponseRedirect(ret_url)
            except AssertionError:
                msg = f"{request.user}, your bid {data['value']} is less than previous {current_bid}."
                logger_views.warning(msg)
                return HttpResponseRedirect(ret_url)
        else:
            msg = "Error. Can not raise bid. Reopen this page. Please, confirm form"
            logger_views.error(msg)
            messages.error(request, msg)
            return HttpResponseRedirect(reverse("auctions:index"))
    else:
        msg = "Can not open this page. Please, confirm form"
        logger_views.error(msg)
        messages.error(request, msg)
        return HttpResponseRedirect(reverse("auctions:index"))


@login_required(login_url=reverse_lazy("auctions:login"))
def change_wishlist(request, pk):
    if request.method == "POST":
        ret_url = request.POST.get('ret_url', '')
        listing = get_object_or_404(Listing, pk=pk)
        exist_in_wishlist = Wishlist.exist_in_wishlist(listing, user=request.user)
        try:
            assert ret_url
            assert listing.active
            if exist_in_wishlist:
                result = Wishlist.delete_from_wishlist(listing, user=request.user)
                try:
                    assert result
                    msg = f"Successfully delete {listing} from wishlist."
                    logger_views.debug(msg)
                    messages.success(request, msg)
                    return HttpResponseRedirect(ret_url)
                except AssertionError:
                    msg = f"Can not delete from user's {request.user} wishlist for listing {listing}"
                    logger_views.error(msg)
                    messages.error(request, msg)
                    return HttpResponseRedirect(reverse("auctions:index"))
            else:
                result = Wishlist.add_to_wishlist(listing, user=request.user)
                try:
                    assert result
                    msg = f"Successfully add {listing} to wishlist."
                    logger_views.debug(msg)
                    messages.success(request, msg)
                    return HttpResponseRedirect(ret_url)
                except AssertionError:
                    msg = f"Can not add to user's {request.user} wishlist for listing {listing}"
                    logger_views.error(msg)
                    messages.error(request, msg)
                    return HttpResponseRedirect(ret_url)
        except AssertionError:
            msg = f"Can not manipulate with user's {request.user} wishlist for listing {listing}"
            logger_views.error(msg)
            messages.error(request, msg)
            return HttpResponseRedirect(reverse("auctions:index"))
    else:
        msg = f"Can not change wishlist. Please, confirm form"
        logger_views.error(msg)
        messages.error(request, msg)
        return HttpResponseRedirect(reverse("auctions:index"))


class WishlistView(generic.ListView):
    context_object_name = 'listing'
    template_name = 'auctions/wishlist.html'

    def get_queryset(self):
        user = self.request.user
        category_filter = self.request.GET.get('f', '')
        if category_filter:
            wish_listings = [wish.listing for wish in Wishlist.objects.filter(user=user,
                                                                              listing__active=True,
                                                                              listing__category__name=category_filter)]
        else:
            wish_listings = [wish.listing for wish in Wishlist.objects.filter(user=user, listing__active=True)]
        ret_url = reverse('auctions:wishlist')
        ret_close_url = ret_url
        result = []
        for listing in wish_listings:
            extra_data = {'ret_url': ret_url,
                          'ret_close_url': ret_close_url,
                          'exist_in_wishlist': Wishlist.exist_in_wishlist(listing, user)
                          }
            result.append(Dataset(listing, extra_data))
        return result

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(WishlistView, self).get_context_data(**kwargs)
        categories = Category.objects.all()
        context['categories'] = categories
        context['category_bage'] = self.request.GET.get('f', '')
        if self.request.user.is_active:
            context['wishlist_bage'] = len(Wishlist.objects.filter(user=self.request.user, listing__active=True))
        else:
            context['wishlist_bage'] = ''
        return context


@login_required(login_url=reverse_lazy("auctions:login"))
def close_listing(request, pk):
    if request.method == "POST":
        ret_url = request.POST.get('ret_url', '')
        try:
            assert pk
            assert ret_url
            listing = get_object_or_404(Listing, pk=pk)
            assert listing.user == request.user
            result = Listing.close_listing(pk)
            assert result
            winner = result.get('user_winner')
            if winner == listing.user:
                msg = f"Unfortunately there is not winner for listing {listing}."
                logger_views.debug(msg)
                messages.warning(request, msg)
                return HttpResponseRedirect(ret_url)
            elif winner:
                msg = f"Successfully close listing {listing}. " \
                      f"Winner is {result['user_winner']} with bid {result['best_bid']} $."
                logger_views.debug(msg)
                messages.success(request, msg)
                # TODO ADD notification for winner
                return HttpResponseRedirect(ret_url)
            else:
                msg = f"Error. Can not find winner."
                logger_views.error(msg)
                messages.error(request, msg)
                return HttpResponseRedirect(ret_url)
        except AssertionError:
            msg = f"Can not delete listing with id = {pk}"
            logger_views.error(msg)
            messages.error(request, msg)
            return HttpResponseRedirect(reverse('auctions:index'))
    else:
        msg = f"Error. Can not close listing."
        logger_views.error(msg)
        messages.error(request, msg)
        return HttpResponseRedirect(reverse('auctions:index'))
