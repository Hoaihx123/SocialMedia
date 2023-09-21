from django.shortcuts import render
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.shortcuts import redirect

from .models import Profile, Post, Like_post, Followcount
from django.contrib.auth.decorators import login_required
import sqlite3

# Create your views here.
@login_required(login_url='signin')
def index(request):
    db = sqlite3.connect('db.sqlite3')
    cur = db.cursor()
    cur.execute(f"SELECT DISTINCT p.user, img, caption, created_time, no_of_like, p.id from core_post p JOIN core_followcount  f on  p.user=f.user where f.follower='{request.user.username}'or p.user='{request.user.username}' order by created_time desc")
    posts = cur.fetchall()
    user_profile = Profile.objects.get(user=request.user)
    sql = "WITH t1 as (SELECT username FROM auth_user f1 WHERE (Select count(*) from core_followcount f2 where follower='"+request.user.username+"' and f1.username=f2.user)=0 and username!='"+request.user.username+"'), \
     t2 as (select username, count(*) as num_fl from t1 left join core_followcount on user=t1.username GROUP BY username) \
     Select t2.username, profileimg, num_fl from t2 join auth_user u on t2.username=u.username \
                      join core_profile p on u.id=p.user_id order by num_fl desc"
    cur.execute(sql)
    followers = cur.fetchall()
    return render(request, 'index.html', {'user_profile': user_profile, 'posts': posts, 'followers': followers})

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']
        if password == password2:
            if User.objects.filter(username=username).exists() or User.objects.filter(email=email).exists():
                messages.info(request, "Email or user was used")
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('setting')
        else:
            messages.info(request, "Password no matching")
            return redirect('signup')
    else:
        return render(request, 'signup.html')
def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, "Username or password incorrect")
            return redirect('signin')
    else:
        return render(request, 'signin.html')
@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')
@login_required(login_url='signin')
def setting(request):
    user_profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
       if request.FILES.get('profileimg') == None:
           profileimg = user_profile.profileimg
           bio = request.POST['bio']
           location = request.POST['location']
           user_profile.profileimg = profileimg
           user_profile.bio = bio
           user_profile.location = location
           user_profile.save()
       if request.FILES.get('profileimg') != None:
           profileimg = request.FILES.get('profileimg')
           bio = request.POST['bio']
           location = request.POST['location']
           user_profile.profileimg = profileimg
           user_profile.bio = bio
           user_profile.location = location
           user_profile.save()
       return redirect('setting')
    else:
       return render(request, 'setting.html', {'user_profile': user_profile})
@login_required(login_url='signin')
def upload(request):
        if request.method == 'POST':
            user = request.user.username
            img = request.FILES.get('img')
            caption = request.POST['caption']
            post = Post.objects.create(user=user, caption=caption, img=img)
            post.save()
            return redirect('/')
        else:
            return redirect('/')
@login_required(login_url='signin')
def like_post(request):
    username = request.user.username
    id_port = request.GET.get('post_id')
    post = Post.objects.get(id=id_port)
    like = Like_post.objects.filter(id_port=id_port, username=username).first()
    if like == None:
        new = Like_post.objects.create(id_port=id_port, username=username)
        new.save()
        post.no_of_like = post.no_of_like+1
        post.save()
        return redirect('/')
    else:
        like.delete()
        post.no_of_like = post.no_of_like-1
        post.save()
        return redirect('/')
@login_required(login_url='signin')
def profile(request, username):

    user_prof = User.objects.get(username=username)
    profile = Profile.objects.get(user=user_prof)
    posts = Post.objects.filter(user=username)
    follower = len(Followcount.objects.filter(user=username))
    following = len(Followcount.objects.filter(follower=username))
    if Followcount.objects.filter(user=username, follower=request.user.username).first() == None:
        button = 'Follow'
    else:
        button = 'Unfollow'
    context = {'profile': profile, 'username': username, 'posts': posts, 'num': len(posts), 'follower': follower, 'following': following, 'button': button}
    return render(request, 'profile.html', context)
@login_required(login_url='signin')
def follow(request):
    if request.method == 'POST':
        user = request.POST['user']
        follower =request.POST['follower']
        fl = Followcount.objects.filter(user=user, follower=follower).first()
        if fl == None:
            fl = Followcount.objects.create(user=user, follower=follower)
            fl.save()
        else:
            fl.delete()
        return redirect('/profile/'+user)
    else:
        return redirect('/')


@login_required(login_url='signin')
def follow_index(request, username):
    follower = request.user.username
    fl = Followcount.objects.create(user=username, follower=follower)
    fl.save()
    return redirect('/')

@login_required(login_url='signin')
def delect_post(request, user, post_id):
    if request.user.username == user:
        p = Post.objects.get(id=post_id)
        p.delete()
        db = sqlite3.connect('db.sqlite3')
        cur = db.cursor()
        cur.executescript(f"delete from core_like_post where id_port='{post_id}'")
        return redirect('/')
    else:
        return redirect('/')
def search(request):
    if request.method == 'POST':
        user_type = request.POST['user_type']
        user_types = User.objects.filter(username__icontains=user_type)
        user_type_profiles = []
        for i in user_types:
            u = Profile.objects.filter(user=i)
            user_type_profiles.append(u)
        return render(request, 'search.html', {'user_type_profiles': user_type_profiles})
    else:
        return redirect('/')