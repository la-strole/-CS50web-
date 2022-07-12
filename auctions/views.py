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

from .models import User, Listing, Wishlist, Category, Comments, Info_msg
from auctions import forms, logger

# Add logger
logger_views = logger.LoggerAuctions('views').logger


class Bages:
    def __init__(self, category):
        self.category = category


class index(generic.ListView):
    """
    View list of all listings (active otr filtered by GET request of category name). Use index.html template.
    """

    model = Listing
    context_object_name = 'listings'
    template_name = 'auctions/index.html'

    def get_queryset(self):
        # Use for category filter
        category_name = self.request.GET.get('f', '')
        if category_name:
            try:
                assert category_name in [item.name for item in Category.objects.all()]
            except AssertionError as e:
                msg = f"Category name ({category_name}) not in categories names"
                logger_views.error(msg)
                messages.error(self.request, msg)
                return HttpResponseRedirect(reverse('auctions:index'))
            listings = Listing.listing_filter_by_category(category_name)
        else:
            listings = Listing.objects.filter(active=True)
        return listings

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(index, self).get_context_data(**kwargs)
        categories = Category.objects.all()
        context['categories'] = categories
        context['bages'] = Bages(category=self.request.GET.get('f', ''))
        return context


class Categories(generic.ListView):
    model = Category
    context_object_name = 'categories'
    template_name = 'auctions/categories.html'


class NotificationsView(generic.ListView):
    model = Info_msg
    context_object_name = 'notifications'
    template_name = 'auctions/notifications.html'

    def get_queryset(self):
        notifications = Info_msg.objects.filter(is_read=False)
        return notifications


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
        return render(request, 'auctions/create_listing.html', {'form': form,
                                                                'categories': None,
                                                                'bages': Bages(category=None)})


class ListingView(generic.DetailView):
    """
    Return listing view for listing_id. Use listing.html template.
    """

    model = Listing
    template_name = 'auctions/listing.html'
    context_object_name = 'listing'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(ListingView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        user = self.request.user
        context['exist_in_wishlist'] = Wishlist.exist_in_wishlist(self.object, user)
        context['categories'] = None
        context['bages'] = Bages(category=None)
        # Add form to comments
        context['comments_form'] = forms.CommentsForm()
        return context

    def get_queryset(self):
        result = Listing.objects.filter(active=True)
        return result


@login_required(login_url=reverse_lazy("auctions:login"))
def raise_bid(request, url, pk):
    if request.method == "POST":
        url = f"/{url}"
        listing = get_object_or_404(Listing, pk=pk)
        populated_form = forms.RaiseBid(request.POST)
        if populated_form.is_valid() and listing.active:
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
                    return HttpResponseRedirect(url)
                else:
                    msg = f"Successfully raise bid for {listing} to {data['value']} $"
                    messages.success(request, msg)
                    return HttpResponseRedirect(url)
            except AssertionError:
                msg = f"{request.user}, your bid {data['value']} is less than previous {current_bid}."
                logger_views.warning(msg)
                return HttpResponseRedirect(url)
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
def change_wishlist(request, url, pk):
    url = f"/{url}"
    if request.method == "POST":
        listing = get_object_or_404(Listing, pk=pk)
        exist_in_wishlist = Wishlist.exist_in_wishlist(listing, user=request.user)
        try:
            assert listing.active
            if exist_in_wishlist:
                result = Wishlist.delete_from_wishlist(listing, user=request.user)
                try:
                    assert result
                    msg = f"Successfully delete {listing} from wishlist."
                    logger_views.debug(msg)
                    messages.success(request, msg)
                    return HttpResponseRedirect(url)
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
                    return HttpResponseRedirect(url)
                except AssertionError:
                    msg = f"Can not add to user's {request.user} wishlist for listing {listing}"
                    logger_views.error(msg)
                    messages.error(request, msg)
                    return HttpResponseRedirect(url)
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


@login_required(login_url=reverse_lazy("auctions:login"))
def wishlist_view(request):
    user = request.user
    category_filter = request.GET.get('f', '')
    categories = Category.objects.all()
    if category_filter:
        if category_filter in [item.name for item in categories]:
            wish_listings = [(wish.listing, Wishlist.exist_in_wishlist(wish.listing, user))
                             for wish in Wishlist.objects.filter(user=user,
                                                                 listing__active=True,
                                                                 listing__category__name=category_filter)]
        else:
            msg = f"Category name in request ({category_filter}) not in category names."
            logger_views.error(msg)
            messages.error(request, msg)
            return HttpResponseRedirect(reverse('wishlist'))
    else:
        wish_listings = [(wish.listing, Wishlist.exist_in_wishlist(wish.listing, request.user))
                         for wish in Wishlist.objects.filter(user=user,
                                                             listing__active=True)]

    bages = Bages(category=category_filter)
    return render(request, template_name='auctions/wishlist.html', context={'bages': bages,
                                                                            'wish_listings': wish_listings,
                                                                            'categories': categories
                                                                            })


@login_required(login_url=reverse_lazy("auctions:login"))
def close_listing(request, url, pk):
    if request.method == "POST":
        if url.startswith('listing'):
            url = '/index'
        else:
            url = f"/{url}"
        try:
            assert pk
            listing = get_object_or_404(Listing, pk=pk)
            assert listing.user == request.user
            result = Listing.close_listing(pk)
            assert result
            winner = result.get('user_winner')
            if winner == listing.user:
                msg = f"Unfortunately there is not winner for listing {listing}."
                logger_views.debug(msg)
                messages.warning(request, msg)
                Info_msg.create_notification(title=f'{msg}',
                                             text=f"You win yourself listing '{listing}'"
                                                  f"with bid={result['best_bid']} $.",
                                             user=result['user_winner'])
                return HttpResponseRedirect(url)
            elif winner:
                msg = f"Successfully close listing {listing}. " \
                      f"Winner is {result['user_winner']} with bid {result['best_bid']} $."
                Info_msg.create_notification(title='You win in auction!',
                                             text=f"Congratulations! You win listing '{listing}' from {listing.user} "
                                                  f"with bid={result['best_bid']} $.",
                                             user=result['user_winner'])
                logger_views.debug(msg)
                messages.success(request, msg)
                return HttpResponseRedirect(url)
            else:
                msg = f"Error. Can not find winner."
                logger_views.error(msg)
                messages.error(request, msg)
                return HttpResponseRedirect(url)
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


@login_required(login_url=reverse_lazy("auctions:login"))
def add_comment(request, pk):
    if request.method == "POST":
        populated_form = forms.CommentsForm(request.POST)
        if populated_form.is_valid():
            data = populated_form.cleaned_data
            listing = get_object_or_404(Listing, id=pk)
            result = Comments.add_comment(listing=listing,
                                          user=request.user,
                                          text=data['text'])
            if result:
                msg = f"Successfully add new comment to {listing}"
                logger_views.debug(msg)
                messages.success(request, msg)
                return HttpResponseRedirect(reverse('auctions:listing', kwargs={'pk': pk}))
            else:
                msg = f"Error, Can not add comment to listing {listing}."
                logger_views.error(msg)
                messages.error(request, msg)
                return HttpResponseRedirect(reverse('auctions:listing', kwargs={'pk': pk}))
        else:
            msg = f"Form is not valid. Try again"
            logger_views.error(msg)
            messages.error(request, msg)
            return HttpResponseRedirect(reverse('auctions:listing', kwargs={'pk': pk}))
    else:
        msg = "Error. Expect POST method. Try to fill form again."
        logger_views.error(msg)
        messages.error(request, msg)
        return HttpResponseRedirect(reverse('auctions:listing', kwargs={'pk': pk}))


@login_required(login_url=reverse_lazy("auctions:login"))
def mark_notification_read(request, pk: int):
    result = Info_msg.make_read(pk)
    if result:
        msg = f"Make message with id={pk} as read for user {request.user}."
        logger_views.debug(msg)
        return HttpResponseRedirect(reverse('auctions:notifications'))
    else:
        msg = f"Can not make message read."
        logger_views.error(f'{msg} for user={request.user}, message_id={pk}.')
        messages.error(request, msg)
        return HttpResponseRedirect(reverse('auctions:notifications'))
