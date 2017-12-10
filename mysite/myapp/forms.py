from django import forms
from models import UserModel,LikeModel,PostModel,CommentModel,PointsModel

class SignUpForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ['email','username','name','password']
        # error_messages = {'username':{'required':'Username is empty'},'password':{'required':'Password is empty'},
        #                  'email':{'required':'email is required'}}

class LoginForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ['username','password']


class PostForm(forms.ModelForm):
    class Meta:
        model = PostModel
        fields = ['image', 'caption']


class LikeForm(forms.ModelForm):
    class Meta:
        model = LikeModel
        fields=['post']


class CommentForm(forms.ModelForm):
    class Meta:
        model = CommentModel
        fields = ['comment_text', 'post']


class LeaderForm(forms.ModelForm):
    class meta:
        model = PointsModel
        fields = ['post']
