from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Profile, Post, LikePost, FollowersCount
from itertools import chain
import random
from core.utilities import Utilities
# Create your views here.


@login_required(login_url="signin")
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    user_following_list = []
    feed = []

    user_following = FollowersCount.objects.filter(
        follower=request.user.username)

    for users in user_following:
        user_following_list.append(users.user)

    # Add self user post to list
    post_self = Post.objects.filter(user=request.user.username)
    feed.append(post_self)

    for usernames in user_following_list:
        feed_list = Post.objects.filter(user=usernames)
        feed.append(feed_list)

    # You can with feed_list, just display posts of following users in screen
    feed_list = list(chain(*feed))

    # Get all posts
    posts = Post.objects.all()

    # User suggestion start
    all_users = User.objects.all()
    user_following_all = []

    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)

    new_suggestions_list = [x for x in list(
        all_users) if (x not in list(user_following_all))]
    current_user = User.objects.filter(username=request.user.username)

    final_suggestions_list = [x for x in list(
        new_suggestions_list) if (x not in list(current_user))]

    random.shuffle(final_suggestions_list)

    username_profile = []
    username_profile_list = []

    for users in final_suggestions_list:
        username_profile.append(users.id)

    for ids in username_profile:
        profile_lists = Profile.objects.filter(id_user=ids)
        username_profile_list.append(profile_lists)

    suggestions_username_profile_list = list(chain(*username_profile_list))

    return render(request, "index.html", {'user_profile': user_profile, 'posts': posts, 'suggestions_username_profile_list': suggestions_username_profile_list[:4]})


@login_required(login_url="signin")
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == 'POST':
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)

        username_profile = []
        username_profile_list = []

        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)

        username_profile_list = list(chain(*username_profile_list))
    return render(request, 'search.html', {'user_profile': user_profile, 'username_profile_list': username_profile_list})


@login_required(login_url="signin")
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(
        post_id=post_id, username=username).first()

    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes = post.no_of_likes + 1
        post.save()
        return redirect('/')
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes - 1
        post.save()
        return redirect('/')


@login_required(login_url="signin")
def delete(request):
    ''' Action delete for posts '''

    # Get current user
    username = request.user.username
    # Get post id sended
    post_id = request.POST.get('post_id')

    # Get target post with user and id filter
    post_filter = Post.objects.filter(
        id=post_id, user=username).first()

    # Check have post or no?
    if post_filter == None:
        print('No access to deleting post!')
        return redirect('/')
    else:
        # Delete post
        post_filter.delete()
        return redirect('/')


@login_required(login_url="signin")
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_post_length = len(user_posts)

    follower = request.user.username
    user = pk

    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text = 'Follow'

    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'button_text': button_text,
        'user_followers': user_followers,
        'user_following': user_following
    }
    return render(request, 'profile.html', context)


@login_required(login_url="signin")
def follow(request):
    if request.method == 'POST':
        follower = request.POST['follower']
        user = request.POST['user']

        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(
                follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/' + user)
        else:
            new_follower = FollowersCount.objects.create(
                follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/' + user)
    else:
        return redirect('/')


@login_required(login_url="signin")
def upload(request):
    if request.method == 'POST':
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']
        new_post = Post.objects.create(user=user, image=image, caption=caption)
        new_post.save()
        return redirect('/')
    else:
        return redirect('/')
    return HttpResponse('<h1>Upload View</h1>')


@login_required(login_url="signin")
def settings(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        # Get passowrds
        password = request.POST.get("password", False)
        password_confirm = request.POST.get("password_confirm", False)

        # Check matching passwords
        if password != password_confirm:
            messages.info(request, "Password Not Matching")
            return redirect("settings")

        # Check image non uploaded
        if request.FILES.get("image") == None:
            image = user_profile.profileimg
        else:
            image = request.FILES.get("image")

        bio = request.POST["bio"]
        location = request.POST["location"]
        phone_number = request.POST["phone_number"]

        # Check phone number is exists?
        if Profile.objects.get(user=request.user).phone_number != phone_number:
            if Profile.objects.filter(phone_number=phone_number).exists():
                messages.info(
                    request, 'Your number already used! Try another.')
                return redirect("settings")

        user_profile.profileimg = image
        user_profile.bio = bio
        user_profile.location = location
        user_profile.phone_number = phone_number
        # Check password field
        if password:
            user = User.objects.get(username=request.user.username)
            user.set_password(password)
            user.save()
        user_profile.save()

        messages.info(request, "Changes is saved!")
        return redirect("settings")

    return render(request, "setting.html", {"user_profile": user_profile})


def forget(request):
    if request.method == 'POST':
        # Get phone number from user
        phone_number = request.POST['phone_number']
        # Check phone number
        if Profile.objects.filter(phone_number=phone_number).exists():
            # Get user id from user profile
            user_id = Profile.objects.filter(
                phone_number=phone_number).first().id_user
            # Get user and create password
            user = User.objects.get(id=user_id)
            util = Utilities()
            # Create new password
            new_password = util.create_password(8)
            # Set new password
            user.set_password(new_password)
            user.save()

            # Send password to user phone number
            message = f'''
            بازیابی رمز در شبکه اجتماعی ایران تم
            رمز جدید شما: {new_password}
            '''
            status = util.send_message(phone_number, message)
            if status == 200:
                messages.info(
                    request, 'New password sended to your phone number.')
                return redirect('forget')
            else:
                messages.info(
                    request, 'Error: Message not sended! ' + status)
            return redirect('forget')
        else:
            messages.info(request, 'Your phone number is not found!')
            return redirect('forget')
    else:
        return render(request, 'forget.html')


def signup(request):

    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        phone_number = request.POST['phone_number']
        password = request.POST["password"]
        password2 = request.POST["password2"]

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, "Email Taken")
                return redirect("signup")
            elif User.objects.filter(username=username).exists():
                messages.info(request, "Username Is Taken")
                return redirect("signup")
            elif Profile.objects.filter(phone_number=phone_number).exists():
                messages.info(
                    request, 'Your number already used! Try another.')
                return redirect("signup")
            else:
                user = User.objects.create_user(
                    username=username, email=email, password=password)
                user.save()

                # Log user in and redirect to settings page
                user_login = auth.authenticate(
                    username=username, password=password)
                auth.login(request, user_login)

                # Create a profile object for the new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(
                    user=user_model, id_user=user_model.id, phone_number=phone_number)
                new_profile.save()
                return redirect('settings')
        else:
            messages.info(request, "Password Not Matching")
            return redirect("signup")
    else:
        return render(request, "signup.html")


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Credentials Invalid')
            return redirect('signin')
    else:
        return render(request, 'signin.html')


@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')
