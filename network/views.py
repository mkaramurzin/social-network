import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django import forms
from django.db.models import OuterRef, Subquery, Count, Exists

from .models import Following, Like, User, Post

MAX_POSTS = 10

class NewPostForm(forms.Form):
    post_text = forms.Field(widget=forms.Textarea(
        {'name': 'text', 'maxlength': 255, 'class': 'form-control', 'id': 'new-text', 'placeholder': "What's happening?"}), label='')

def index(request):

    if request.method == 'POST':
        form = NewPostForm(request.POST)
        if form.is_valid():
            Post.objects.create(
                user = request.user,
                text = form.cleaned_data["post_text"]
            )
            return HttpResponseRedirect(reverse('index'))

    if request.user.is_authenticated:
        likes = Like.objects.filter(post=OuterRef('id'), user_id=request.user)
        posts = Post.objects.filter().order_by(
            '-timestamp').annotate(current_like=Count(likes.values('id')))
    else:
        posts = Post.objects.order_by("-timestamp").all()
    paginator = Paginator(posts, MAX_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {
        "posts": page_obj,
        "form": NewPostForm()
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

def profile(request, username):

    profile_user = User.objects.get(username=username)

    if request.user.is_authenticated:
        likes = Like.objects.filter(post=OuterRef('id'), user_id=request.user)
        posts = Post.objects.filter(user=profile_user).order_by(
            '-timestamp').annotate(current_like=Count(likes.values('id')))
        following = Following.objects.filter(follower=request.user, following=profile_user).count()
    else:
        posts = Post.objects.filter(user=profile_user).order_by("-timestamp").all()
        following = 0

    paginator = Paginator(posts, MAX_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    followers = Following.objects.filter(following=profile_user).count()
    follow_count = Following.objects.filter(follower=profile_user).count()

    return render(request, "network/user.html", {
        "user": profile_user,
        "posts": page_obj,
        "followers": followers,
        "total_posts": Post.objects.filter(user=profile_user).count(),
        "is_following": following > 0,
        "following": follow_count
    })

def like(request, id):
    post = Post.objects.get(id=id)
    like = Like.objects.get_or_create(user=request.user, post=post)
    css_class = 'fas fa-heart'

    # if like already exists
    if not like[1]:
        css_class = 'far fa-heart'
        Like.objects.filter(user=request.user, post=post).delete()
    
    likes = Like.objects.filter(post=post).count()

    return JsonResponse({
        "like": id, "css_class": css_class, "likes": likes
    })

def follow(request, id):

    result = 'Follow'
    user_follower = User.objects.get(id=id)
    follower = Following.objects.get_or_create(
        follower=request.user, following=user_follower)
    if not follower[1]:
        Following.objects.filter(
            follower=request.user, following=user_follower).delete()
        result = 'Unfollow'
    total_followers = Following.objects.filter(
        following=user_follower).count()

    return JsonResponse({"result": result, "followers": total_followers})

def following(request):

    if not request.user.is_authenticated:
        return HttpResponseRedirect('login')

    following = Following.objects.filter(follower=request.user)
    posts = Post.objects.filter(user_id__in=following.values('following_id')).order_by('-timestamp').all()
    
    likes = Like.objects.filter(post=OuterRef('id'), user_id=request.user)
    posts = posts.annotate(current_like=Count(likes.values('id')))

    paginator = Paginator(posts, MAX_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "posts": page_obj,
    })

@csrf_exempt
def edit(request):
    data = json.loads(request.body)

    post = Post.objects.get(id=data.get("id", ""))

    post.text = data.get("new_text", "")
    post.save()

    return JsonResponse({"message": "Post edited successfully.", "text": post.text})