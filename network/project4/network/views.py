from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .models import User, Post
from .forms import NewPostForm

import datetime

def index(request):
    return render(request, "network/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@require_http_methods(["POST"])
def api_new_post(request):
    if request.user.is_authenticated:
        form = NewPostForm(request.POST)
        if form.is_valid():
            post = Post(
                post_text = request.POST.get("newPostText"),
                author = request.user,
                timestamp = datetime.datetime.now()
            )
            post.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'errors': form.errors})
    else:
        return HttpResponseRedirect(reverse("index"))
    
def api_posts_list(request):
    # Get 10 latest posts
    ten_last_posts = Post.objects.all()[:10]
    response = [post.get_post_json() for post in ten_last_posts]
    return JsonResponse({"response": response})