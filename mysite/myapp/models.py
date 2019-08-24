# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.validators import RegexValidator
from django.db import models
import uuid

# Create your models here.
class UserModel(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=255)
    username = models.CharField(max_length=120)
    """
            validators=[
            RegexValidator(
                regex='^.{4,}.$',
                message='Username must be 4 character long',
                code='invalid_username'
                    ),
                ]
            )#,unique=True)
    """
    password = models.CharField(max_length=40)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)



class PostModel(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.PROTECT)

    image = models.FileField(upload_to='user_images')
    image_url = models.CharField(max_length=255)
    caption = models.CharField(max_length=240)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    @property
    def like_count(self):
      return len(LikeModel.objects.filter(post=self))
    @property
    def comments(self):
        return CommentModel.objects.filter(post=self).order_by('created_on')
    @property
    def points(self):
        return PointsModel.objects.get(post=self).point


class SessionToken(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.PROTECT)
    session_token = models.CharField(max_length=255)
    last_request_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)
    def create_token(self):
        self.session_token = uuid.uuid4()


class LikeModel(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.PROTECT)
    post = models.ForeignKey(PostModel, on_delete=models.PROTECT)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)


class CommentModel(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.PROTECT)
    post = models.ForeignKey(PostModel, on_delete=models.PROTECT)
    comment_text = models.CharField(max_length=555)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

class PointsModel(models.Model):
    post = models.ForeignKey(PostModel, on_delete=models.PROTECT)
    point = models.FloatField(max_length=10)




