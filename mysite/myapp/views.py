# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from clarifai.rest import ClarifaiApp
from sendgrid.helpers.mail import *
import sendgrid
from django.shortcuts import render,redirect
from forms import SignUpForm,LoginForm,PostForm,LikeForm,CommentForm,LeaderForm
from django.contrib.auth.hashers import make_password,check_password
from models import UserModel,SessionToken,PostModel,LikeModel,CommentModel,PointsModel
from datetime import timedelta
from django.utils import timezone
from imgurpython import ImgurClient
from mysite.settings import BASE_DIR
from details import client_id,client_secret,sendgrid_api,clarifai_api

# Create your views here.
def signup_view(request):
    dict = {}
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            if len(username) >= 4:
                name = form.cleaned_data['name']
                email = form.cleaned_data['email']
                password = form.cleaned_data['password']
                if len(password) >= 5:
                    # SQL QUERY
                    user = UserModel(name=name, password=make_password(password), email=email, username=username)
                    user.save()
                    #welcome email to the user for successfully completing the sign up
                    sg = sendgrid.SendGridAPIClient(apikey=sendgrid_api)
                    from_email = Email("varontyagi@gmail.com")
                    to_email = Email(email)
                    subject = "Upload to win"
                    content = Content("text/plain", "you are successfully signed up!! Enjoy")
                    mail = Mail(from_email, subject, to_email, content)
                    sg.client.mail.send.post(request_body=mail.get())

                    return render(request, 'success.html')
                else:
                    dict['message'] = "Password to be at least 5 characters long !"
            else:
                dict['message'] = "Username to be at least 4 characters long !"
        else:
            dict['message'] = "Invalid Fields! Re-enter above fields."
            #dict['message'] = form.errors

    else:
        form = SignUpForm()

    dict['form'] = form
    return render(request, 'index.html', dict)


def login_view(request):
    dict = {}
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            #SQL QUERY
            user = UserModel.objects.filter(username=username).first()
            if not user:
                dict['message'] = 'Incorrect username or password! Please try again!'
            else:
                # Check for the password
                if not check_password(password, user.password):
                    dict['message'] = 'Incorrect password or username! Please try again!'
                else:
                    token = SessionToken(user=user)
                    token.create_token()
                    token.save()
                    response = redirect('/feed/')
                    response.set_cookie(key='session_token', value=token.session_token)
                    return response
        else:
            dict['message'] = "Incorrect password or username! Please try again!"
    else:
        form = LoginForm()

    dict['form'] = form
    return render(request, 'login.html', dict)


def feed_view(request):
    user = check_validation(request)
    if user:
        posts = PostModel.objects.all().order_by('-created_on')
        """
        if request.method == 'GET':    
            name = request.GET.get('q','')
            posts = PostModel.objects.all().order_by('-created_on')
            if (name != ''):
                for post in posts:
                    if post.user.username != name:
                        post.delete()
        """
        for post in posts:
            existing_like = LikeModel.objects.filter(post=post, user=user).first()
            if existing_like:
                post.has_liked = True
        return render(request, 'feed.html', {'posts': posts})
    else:
        return redirect('/login/')


def post_view(request):
    user = check_validation(request)
    dict = {}
    if user:
        if request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                image = form.cleaned_data.get('image')
                caption = form.cleaned_data.get('caption')
                post = PostModel(user=user, image=image, caption=caption)
                post.save()

                path = str(BASE_DIR + '/' + post.image.url)
                client = ImgurClient(client_id, client_secret)
                post.image_url = client.upload_from_path(path, anon=True)['link']
                post.save()

                app = ClarifaiApp(api_key=clarifai_api)
                model = app.models.get('logo')
                response = model.predict_by_url(url=post.image_url)
                try:
                    val = float(response['outputs'][0]['data']['regions'][0]['data']['concepts'][0]['value']) * 10
                    val = float("%.2f" % (val))
                except:
                    val = 7.55
                else:
                    pass

                point = PointsModel(post=post, point=val)
                point.save()

                return redirect('/feed/')

        else:
            form = PostForm()

        dict['form'] = form
        return render(request, 'post.html', dict)

    else:
        return redirect('/login/')


def like_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = LikeForm(request.POST)
        if form.is_valid():
            post = form.cleaned_data.get('post')
            email = post.user.email
            #post_id = post
            existing_like = LikeModel.objects.filter(post=post, user=user).first()
            if not existing_like:
                LikeModel.objects.create(post=post, user=user)
                # welcome email to the user for successfully completing the sign up
                sg = sendgrid.SendGridAPIClient(apikey=sendgrid_api)
                from_email = Email("varontyagi@gmail.com")
                to_email = Email(email)
                subject = "Upload to win"
                content = Content("text/plain", user.name + " has liked your post")
                mail = Mail(from_email, subject, to_email, content)
                sg.client.mail.send.post(request_body=mail.get())
            else:
                existing_like.delete()

            return redirect('/feed/')
    else:
       return redirect('/login/')


def comment_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            post = form.cleaned_data.get('post')
            email = post.user.email
            comment_text = form.cleaned_data.get('comment_text')
            comment = CommentModel.objects.create(user=user, post=post, comment_text=comment_text)
            comment.save()

            sg = sendgrid.SendGridAPIClient(apikey=sendgrid_api)
            from_email = Email("varontyagi@gmail.com")
            to_email = Email(email)
            subject = "Upload to win"
            content = Content("text/plain", user.name + " has commented on your post")
            mail = Mail(from_email, subject, to_email, content)
            sg.client.mail.send.post(request_body=mail.get())
            return redirect('/feed/')

        else:
            return redirect('/feed/')
    else:
        return redirect('/login')


def leaders_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        test = 0.0
        points = PointsModel.objects.all()
        if points:
            for point in points:
                if (test < point.point):
                    value = point
            return render(request, 'leadersboard.html', {'points': points, 'value': value})
        else:
            return redirect('/feed/')
    else:
        return redirect('/feed/')


def logout_view(request):
    if request.method == 'GET':
        if request.COOKIES.get('session_token'):
            SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first().delete()
        return redirect('/login/')
    else:
        return redirect('/feed/')


def check_validation(request):
    if request.COOKIES.get('session_token'):
        session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
        if session:
            time_to_live = session.created_on + timedelta(days=1)
            if time_to_live > timezone.now():
                return session.user
    else:
        return None