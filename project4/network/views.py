from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django import forms
from django.core.paginator import Paginator
import json
from .models import User, Post

class NewPostForm(forms.Form):
    post_content = forms.CharField(label="", max_length=255, required=True, widget=forms.TextInput(attrs={'placeholder': "What's on your mind...", 'class': 'form-control', 'id':'new-post-content'}))


def index(request):
    if request.method == "POST":
        form = NewPostForm(request.POST)
        if form.is_valid():
            new_post_content = form.cleaned_data["post_content"]

            new_post = Post(content=new_post_content, user=request.user)
            new_post.save()
        else:
            posts = Post.objects.all()
            posts = posts.order_by("-timestamp").all() 

            return render(request, "network/index.html", {
                "posts": posts,
                "form": form
            })

    posts = Post.objects.all()
    posts = posts.order_by("-timestamp").all()

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    posts= paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "posts": posts,
        "form": NewPostForm()
    })


@csrf_exempt
def view_post(request, post_id):
    # Try to find the given post
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    # Give posts' content
    if request.method == "GET":
        return JsonResponse(post.serialize())

    # Update post's likes when liked, or content when edited
    elif request.method == "PUT":
        data = json.loads(request.body)
        if data.get("likes") is not None:
            post.likes = data["likes"]
        if data.get("liked_by") is not None:
            liked_by = data["liked_by"].split(",")

            if '' in liked_by:
                liked_by = []

            for user in post.liked_by.all():
                post.liked_by.remove(user)
            for user in liked_by:
                post.liked_by.add(user)
        if data.get("content") is not None:
            post.content = data["content"]
        post.save()
        return HttpResponse(status=204)

    # Must be PUT or GET request
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)


def view_profile(request, person_id):
    profile = User.objects.get(pk=person_id)

    posts = Post.objects.filter(user = person_id)
    posts = posts.order_by("-timestamp").all()

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    posts= paginator.get_page(page_number)

    followers = 0
    all_users = User.objects.all()
    for user in all_users:
        if profile in user.following.all():
            followers += 1

    return render(request, "network/view_profile.html", {
        "profile":profile,
        "posts":posts,
        "followers":followers
    })


@csrf_exempt
def follow_profile(request, user_id):
    # Try to find the given user
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found."}, status=404)

    # Give posts' content
    if request.method == "GET":
        return JsonResponse(user.serialize())

    # Update post's likes when liked, or content when edited
    elif request.method == "PUT":
        data = json.loads(request.body)
        if data.get("following") is not None:
            following = data["following"].split(",")

            if '' in following:
                following = []

            for follower in user.following.all():
                user.following.remove(follower)
            for follower in following:
                user.following.add(follower)
        user.save()
        return HttpResponse(status=204)

    # Must be PUT or GET request
    else:
        return JsonResponse({
            "error": "GET or PUT request required."
        }, status=400)


@login_required
def following_posts(request):
    followed_users = request.user.following.all()

    posts = Post.objects.filter(user__in= followed_users)
    posts = posts.order_by("-timestamp").all()

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    posts= paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "posts":posts
    })


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
