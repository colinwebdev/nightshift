from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from uuid import uuid4
from django.core.files import File
from urllib.request import urlopen
from tempfile import NamedTemporaryFile

def processUpload(instance, filename):
    fileExt = filename.split('.')[-1]
    newFileName = '{}.{}'.format(uuid4().hex, fileExt)
    return "user_{0}/{1}".format(instance.user.id, newFileName)

def processAvatar(instance, filename):
    fileExt = filename.split('.')[-1]
    newFileName = '{}.{}'.format(uuid4().hex, fileExt)
    return "user_{0}/{1}".format(instance.id, newFileName)

class User(AbstractUser):
    avatar = models.ImageField(null=True, upload_to=processAvatar)
    pronouns = models.TextField(null=True)
    bio = models.TextField(null=True)
    title = models.TextField(null=True)

class Post(models.Model):
    POST_TYPE_CHOICES = [
        ("blog", "blog"),
        ("image", "image"),
        ("writing", "writing")
    ]
    postType = models.CharField(max_length=10, choices=POST_TYPE_CHOICES, default='image')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(null=True, upload_to=processUpload)
    postTitle = models.TextField(null=True)
    postBody = models.TextField()
    timePosted = models.DateTimeField(auto_now_add=True)
    timeEdited = models.DateTimeField(auto_now=True)
    isArchived = models.BooleanField(default=False)
    isDeleted = models.BooleanField(default=False)
    archivedDate = models.DateTimeField(null=True)
    deletedDate = models.DateTimeField(null=True)

class Tag(models.Model):
    tagText = models.TextField()
    slug = models.TextField(unique=True)
    addedBy = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    addedDate = models.DateTimeField(auto_now_add=True)

class PostTags(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

class Follows(models.Model):
    followSource = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followSource')
    followTarget = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followTarget')
    dateAdded = models.DateTimeField(auto_now_add=True)

class Favorites(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    dateAdded = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.TextField()
    dateAdded = models.DateTimeField(auto_now_add=True)

class ProfileComment(models.Model):
    profile = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profile')
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commenter')
    text = models.TextField()
    dateAdded = models.DateTimeField(auto_now_add=True)


