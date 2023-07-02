from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django import forms
from django import template
from django.template.defaultfilters import stringfilter
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from random import randint

from .models import *
from .loadData import makeUsers, makePosts, makeFollows, makeLikes, makeComments, makeProfileComments

# register = template.Library()
popularPosts = []

class NewPostForm(forms.Form):
    title = forms.CharField(label="Title", label_suffix="")
    body = forms.CharField(widget=forms.Textarea(attrs={'rows':'20'}),
                           label="Body", label_suffix="")
    tags = forms.CharField(widget=forms.Textarea(attrs={'rows':'5'}),
                           label="Tags", required=False, label_suffix="")
    
class ImagePostForm(NewPostForm):
    image = forms.FileField(widget=forms.FileInput(attrs={'accept':'image/*'}), label="Image", label_suffix="")

class EditUserForm(forms.Form):
    username = forms.CharField(label="Username", label_suffix="")
    avatar = forms.FileField(widget=forms.FileInput(attrs={'accept':'image/*'}), label="Avatar", label_suffix="", required=False)
    title = forms.CharField(label="User Title", label_suffix="", required=False)
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows':'10'}),
                           label="Bio", label_suffix="", required=False)
    pronouns = forms.CharField(label="Pronouns", required=False)

def index(request):
    posts = getPosts(Post.objects.order_by('-timePosted').exclude(postType='blog'))
    blogs = getPosts(Post.objects.order_by('-timePosted').filter(postType='blog')[:24])
    paginator = Paginator(posts, 24)
    popularPosts = getFooter()
    page = request.GET.get('page')
    if not page:
        page = 1
    page_range = paginator.get_page(page)
    return render(request, 'gallery/index.html', {
        "page": page_range,
        "blogs": blogs,
        "popular": popularPosts
    })


def register(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "gallery/register.html", {
                "message": "Username already taken.",
                "popular": popularPosts
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "gallery/register.html", {
            "popular": popularPosts
        })
    

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "gallery/login.html", {
                "message": "Invalid username and/or password.",
                "popular": popularPosts
            })
    else:
        return render(request, "gallery/login.html", {
            "popular": popularPosts
        })
    
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

@login_required
def editUser(request, username):
    getUser = User.objects.get(username=username)
    form = EditUserForm(initial={
        "title": getUser.title,
        "bio": getUser.bio,
        "pronouns": getUser.pronouns,
        "avatar": getUser.avatar,
        "username": getUser.username,
    })

    if request.method == 'POST':
        formData = request.POST
        getUser.username = formData['username']
        getUser.title = formData['title']
        getUser.bio = formData['bio']
        getUser.pronouns = formData['pronouns']
        if len(request.FILES) != 0:
            getUser.avatar = request.FILES['avatar']

        try: 
            getUser.save()
            return HttpResponseRedirect(reverse("user", args=[getUser.username]))
        except:
            form = EditUserForm(initial={
                "title": formData['title'],
                "bio": formData['bio'],
                "pronouns": formData['pronouns'],
                "avatar": getUser.avatar,
                "username": formData['username'],
                "popular": popularPosts
            })
            return render(request, "gallery/editUser.html", {
                "form": form,
                "profile": getUser,
                "message": "Could not save profile",
                "popular": popularPosts
            })
    return render(request, "gallery/editUser.html", {
        "form": form,
        "profile": getUser,
        "popular": popularPosts
    })

@login_required
def newPost(request, postType):
    if request.method == 'POST':
        user = getUser(request).id
        formData = request.POST
        title = formData['title']
        body = formData['body']
        tags = formData['tags']
        entry = ''
        if postType == 'image':
            image = request.FILES['image']
            entry = Post(postType=postType, user=User(id=user), postTitle=title, postBody=body, image=image)
        else:
            entry = Post(postType=postType, user=User(id=user), postTitle=title, postBody=body)
        try:
            entry.save()
            entryPosted = Post.objects.latest('id')
            if tags != '':
                tagsArr = tags.split(',')
                for tag in tagsArr:
                    slug = tag.strip().replace(' ', '-')
                    tagID = ''
                    try:
                        tagID = Tag.objects.get(slug=slug)
                    except ObjectDoesNotExist:
                        if tag != '':
                            addTag = Tag(tagText=tag, slug=slug, addedBy=User(id=user))
                            addTag.save()
                            tagID = Tag.objects.latest('id')
                    postTag = PostTags(post=Post(id=entryPosted.id),tag=Tag(id=tagID.id))
                    postTag.save()
            message = 'Post saved'
        except:
            message = 'Could not create post.'
            form = ''
            if postType == 'image':
                form = ImagePostForm(initial={
                    "title": title,
                    "body": body,
                    "tags": tags
                })
            else:
                form = NewPostForm(initial={
                    "title": title,
                    "body": body,
                    "tags": tags
                })
            return render(request, "gallery/newPost.html", {
                "postType": postType,
                "form": form,
                "message": message,
                "popular": popularPosts
            })
        return HttpResponseRedirect(reverse("post", args=[entryPosted.id]))
    form = ''
    if postType == 'image':
        form = ImagePostForm()
    else:
        form = NewPostForm()
    return render(request, "gallery/newPost.html", {
        "postType": postType,
        "form": form,
        "popular": popularPosts
    })

def post(request, postID):
    user = getUser(request)
    post = getSinglePost(Post.objects.get(id=postID), user)
    if request.method == 'POST':
        user = getUser(request).id
        formData = request.POST
        comment = formData['comment']
        entry = Comment(post=Post(id=postID), user=User(id=user), text=comment)
        try:
            entry.save()
            return render(request, 'gallery/post.html', {
                "post": post,
                "message": "Comment added successfully",
                "popular": popularPosts
            })
        except:
            return render(request, 'gallery/post.html', {
                "post": post,
                "text": comment,
                "message": "Comment could not be saved, please try again",
                "popular": popularPosts
            })
    return render(request, 'gallery/post.html', {
        "post": post,
        "popular": popularPosts
    })

@login_required
def deletePost(request, postID):
    post = Post.objects.get(id=postID)
    try:
        post.delete()
        return HttpResponseRedirect(reverse("index"))
    except:
        user = getUser(request)
        returnPost = getSinglePost(post, user)
        return render (request, 'gallery/post.html', {
            "post": returnPost,
            "message": "Could not delete post"
        })

def deleteComment(request, commentID):
    comment = Comment.objects.get(id=commentID)
    try:
        comment.delete()
        return HttpResponseRedirect(reverse("post", args=[comment.post.id]))
    except:
        user = getUser(request)
        post = Post.objects.get(id=comment.post.id)
        returnPost = getSinglePost(post, user)
        return render (request, 'gallery/post.html', {
            "post": returnPost,
            "message": "Could not delete post"
        })


def userGallery(request, username):
    profile = User.objects.get(username=username)
    user = getUser(request)
    images = getPosts(Post.objects.filter(user=profile.id, postType='image').order_by('-timePosted'))
    isFollowedBy = Follows.objects.filter(followTarget=profile.id)
    paginator = Paginator(images, 24)
    pagenum = request.GET.get('page')
    if not pagenum:
        pagenum = 1
    page = paginator.get_page(pagenum)
    profileData = {
        "profile": profile,
        "page": page,
        "view": "posts",
        "header": "Gallery",
        "popular": popularPosts
    }
    if user != None:
        for follow in isFollowedBy:
            if follow.followSource.id == user.id:
                profileData['isFollowingUser'] = 'isFollowingUser'
    return render(request, 'gallery/profileView.html', {
        "profileData": profileData,
        "popular": popularPosts
    })

def userWriting(request, username):
    profile = User.objects.get(username=username)
    user = getUser(request)
    writing = getPosts(Post.objects.filter(user=profile.id, postType='writing').order_by('-timePosted'))
    isFollowedBy = Follows.objects.filter(followTarget=profile.id)
    paginator = Paginator(writing, 24)
    page = request.GET.get('page')
    if not page:
        page = 1
    page_range = paginator.get_page(page)
    profileData = {
        "profile": profile,
        "page": page_range,
        "view": "posts",
        "header": "Writing",
        "popular": popularPosts
    }
    if user != None:
        for follow in isFollowedBy:
            if follow.followSource.id == user.id:
                profileData['isFollowingUser'] = 'isFollowingUser'
    return render(request, 'gallery/profileView.html', {
        "profileData": profileData,
        "popular": popularPosts
    })

def userBlogs(request, username):
    profile = User.objects.get(username=username)
    user = getUser(request)
    blogs = getPosts(Post.objects.filter(user=profile.id, postType='blog').order_by('-timePosted'))
    isFollowedBy = Follows.objects.filter(followTarget=profile.id)
    paginator = Paginator(blogs, 24)
    pagenum = request.GET.get('page')
    if not pagenum:
        pagenum = 1
    page = paginator.get_page(pagenum)
    profileData = {
        "profile": profile,
        "images": page,
        "view": "posts",
        "header": "Blogs",
        "popular": popularPosts
    }
    if user != None:
        for follow in isFollowedBy:
            if follow.followSource.id == user.id:
                profileData['isFollowingUser'] = 'isFollowingUser'
    return render(request, 'gallery/profileView.html', {
        "profileData": profileData,
        "popular": popularPosts
    })

def userLikes(request, username):
    profile = User.objects.get(username=username)
    user = getUser(request)
    getLikes = []
    for like in Favorites.objects.filter(user=profile.id).select_related():
        getLikes.append(like.post)
    likes = getPosts(getLikes)    
    isFollowedBy = Follows.objects.filter(followTarget=profile.id)
    paginator = Paginator(likes, 24)
    pagenum = request.GET.get('page')
    if not pagenum:
        pagenum = 1
    page = paginator.get_page(pagenum)
    profileData = {
        "profile": profile,
        "images": page,
        "view": "posts",
        "header": "Likes",
        "popular": popularPosts,
        "page": page
    }
    if user != None:
        for follow in isFollowedBy:
            if follow.followSource.id == user.id:
                profileData['isFollowingUser'] = 'isFollowingUser'
    return render(request, 'gallery/profileView.html', {
        "profileData": profileData,
        "popular": popularPosts
    })

def userFollowing(request, username):
    profile = User.objects.get(username=username)
    user = getUser(request)
    isFollowing = Follows.objects.filter(followSource=profile.id)
    isFollowedBy = Follows.objects.filter(followTarget=profile.id)
    paginator = Paginator(isFollowing, 100)
    pagenum = request.GET.get('page')
    if not pagenum:
        pagenum = 1
    page = paginator.get_page(pagenum)
    profileData = {
        "profile": profile,
        "isFollowing": page,
        "view": "users",
        "header": "Following",
        "popular": popularPosts
    }
    if user != None:
        for follow in isFollowedBy:
            if follow.followSource.id == user.id:
                profileData['isFollowingUser'] = 'isFollowingUser'
    return render(request, 'gallery/profileView.html', {
        "profileData": profileData,
        "popular": popularPosts
    })

def userFollowers(request, username):
    profile = User.objects.get(username=username)
    user = getUser(request)
    isFollowing = Follows.objects.filter(followSource=profile.id)
    isFollowedBy = Follows.objects.filter(followTarget=profile.id)
    paginator = Paginator(isFollowedBy, 100)
    pagenum = request.GET.get('page')
    if not pagenum:
        pagenum = 1
    page = paginator.get_page(pagenum)
    profileData = {
        "profile": profile,
        "isFollowing": page,
        "view": "users",
        "header": "Followers",
        "popular": popularPosts
    }
    if user != None:
        for follow in isFollowedBy:
            if follow.followSource.id == user.id:
                profileData['isFollowingUser'] = 'isFollowingUser'
    return render(request, 'gallery/profileView.html', {
        "profileData": profileData,
        "popular": popularPosts
    })

def user(request, username):
    profile = User.objects.get(username=username)
    images = getPosts(Post.objects.filter(user=profile.id, postType='image').order_by('-timePosted')[:8])
    writing = getPosts(Post.objects.filter(user=profile.id, postType='writing').order_by('-timePosted')[:8])
    blogs = getPosts(Post.objects.filter(user=profile.id, postType='blog').order_by('-timePosted')[:24])
    comments = ProfileComment.objects.filter(profile=profile.id).order_by('-dateAdded')
    getLikes = []
    for like in Favorites.objects.filter(user=profile.id).select_related()[:8]:
        getLikes.append(like.post)
    likes = getPosts(getLikes)    

    isFollowing = Follows.objects.filter(followSource=profile.id)[:18]
    isFollowedBy = Follows.objects.filter(followTarget=profile.id)[:18]

    user = getUser(request)

    profileData = {
        "profile": profile,
        "images": images,
        "writing": writing,
        "blogs": blogs,
        "comments": comments,
        "likes": likes,
        "isFollowing": isFollowing,
        "isFollowedBy": isFollowedBy,
        "popular": popularPosts
    }
    if user != None:
        for follow in isFollowedBy:
            if follow.followSource.id == user.id:
                profileData['isFollowingUser'] = 'isFollowingUser'
    if request.method == 'POST':
        user = getUser(request).id
        formData = request.POST
        comment = formData['comment']
        entry = ProfileComment(profile=User(id=profile.id), commenter=User(id=user), text=comment)
        try:
            entry.save()
            render(request, 'gallery/profile.html', {
                "profileData": profileData,
                "message": "Commented added",
                "popular": popularPosts
            })
        except:
            return render(request, 'gallery/profile.html', {
                "profileData": profileData,
                "message": "Comment could not be saved, please try again",
                "popular": popularPosts
            })
    return render(request, 'gallery/profile.html', {
        "profileData": profileData,
        "popular": popularPosts
    })

def tag (request, tagSlug):
    tag = Tag.objects.get(slug=tagSlug)
    tagged = PostTags.objects.filter(tag=tag.id)
    postsArr = []
    for item in tagged:
        postsArr.append(item.post.id)
    postsDB = Post.objects.filter(id__in=postsArr).order_by('-timePosted')
    posts = getPosts(postsDB)
    paginator = Paginator(posts, 24)
    pagenum = request.GET.get('page')
    if not pagenum:
        pagenum = 1
    page = paginator.get_page(pagenum)
    page.adjusted_elided_pages = paginator.get_elided_page_range(page)
    return render(request, 'gallery/tag.html', {
        "page": page,
        "tagText": tag.tagText,
        "popular": popularPosts
    })

def loadData(request):
    if request.method == 'POST':
        addedData = ''
        formData = request.POST

        formType = formData['formType']
        num = formData['number']
        if num == '':
            num = 0
        else:
            num = int(num)

        if formType == 'users':
            addedData = makeUsers(num)
        if formType == 'gallery' or formType == 'blog' or formType == 'writing':
            user = formData['user']
            addedData = makePosts(num, user, formType)
        if formType == 'follows':
            addedData = makeFollows(num)
        if formType == 'likes':
            addedData = makeLikes(num)
        if formType == 'comments':
            user = formData['user']
            addedData = makeComments(num, user)
        if formType == 'profileComments':
            user = formData['user']
            addedData = makeProfileComments(num, user)

        processedData = {
            "entries": addedData[0],
            "addedRows": addedData[1],
            "table": formType
        }
        return render(request, 'gallery/loadData.html', {
            "processedData": processedData,
            "status": True
        })
    return render(request, 'gallery/loadData.html')


def getUser(request):
    user = None
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user.username)
    return user

def getPosts(postObj):
    posts = []
    for post in postObj:
        postData = {
            "title": post.postTitle,
            "body": post.postBody,
            "date": post.timePosted,
            "id": post.id,
            "userID": post.user.id,
            "username": post.user.username
        }
        if post.postType == 'image' and post.image:
                postData['image'] = post.image.url
        posts.append(postData)
    return posts

def getSinglePost(postObj, user):
    post = {
        "title": postObj.postTitle,
        "body": postObj.postBody,
        "date": postObj.timePosted,
        "edited": postObj.timeEdited,
        "id": postObj.id,
        "userID": postObj.user.id,
        "username": postObj.user.username,
        "user": User.objects.get(id=postObj.user.id)
    }
    getLikes = Favorites.objects.filter(post=postObj.id)
    post['comments'] = Comment.objects.filter(post=postObj.id).order_by('-dateAdded')
    post['likes'] = len(getLikes)
    if user != None:
        likeCheck = getLikes.filter(user=user.id)
        if len(likeCheck) > 0:
            post['liked'] = 'liked'
    if postObj.postType == 'image' and postObj.image:
        post['image'] = postObj.image.url
    tagsDB = PostTags.objects.filter(post=postObj.id)
    tags = []
    for tag in tagsDB:
        print(f'Tag: {tag.tag.id}')
        getTag = Tag.objects.get(id=tag.tag.id)
        if getTag.tagText != '':
            tags.append(getTag)
    post['tags'] = tags
    return post

@csrf_exempt
def unlike(request, postID):
    if request.method == "PUT":
        data = json.loads(request.body)
        user = data.get('user')
        postLiked = Favorites.objects.get(post=postID, user=user)
        postLiked.delete()
        return HttpResponse(status=204)

@csrf_exempt
def like(request, postID):
    if request.method == "PUT":
        data = json.loads(request.body)
        user = data.get('user')
        entry = Favorites(user=User(id=user), post=Post(id=postID))
        entry.save()
        return HttpResponse(status=204)
    
@csrf_exempt
def follow(request, username):
    if request.method == "PUT":
        data = json.loads(request.body)
        source = data.get('source')
        target = User.objects.get(username=username)
        entry = Follows(followSource=User(id=source), followTarget=User(id=target.id))
        entry.save()
        return HttpResponse(status=204)

@csrf_exempt
def unfollow(request, username):
    if request.method == "PUT":
        data = json.loads(request.body)
        source = data.get('source')
        target = User.objects.get(username=username)
        postLiked = Follows.objects.get(followSource=source, followTarget=target.id)
        postLiked.delete()
        return HttpResponse(status=204)

@csrf_exempt
def updatePost(request, postID):
    if request.method == "PUT":
        data = json.loads(request.body)
        count = data.get('likeCount')
        post = ''
        try:
            post = Post.objects.get(id=postID)
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found"}, status=404)
        try:
            post.likeCount = count
            post.save()
        except: 
            return JsonResponse({"error": "Could not update post count"}, status=405)
        return HttpResponse(status=204)
    
def getFooter():
    getAll = Post.objects.exclude(postType='blog')
    # popValues = []
    popularPosts = []
    while len(popularPosts) < 10:
        num = randint(0, len(getAll) - 1)
        # print(getAll[num])
        popularPosts.append(getAll[num])

    # for item in getAll:
    #     likes = len(Favorites.objects.filter(post=item['id']))
    #     comments = len(Comment.objects.filter(post=item['id']))
    #     value = comments * 5 + likes * 3
    #     popValues.append({
    #         "postID": item['id'],
    #         "popValue": value
    #     })
    # popular = sorted(popValues, key=lambda i: i['popValue'], reverse=True)
    # popular = popular[:9]
    # popularPosts = []
    # for item in popular:
    #     post = Post.objects.get(id=item['postID'])
    #     popularPosts.append(post)
    return popularPosts

popularPosts = getFooter()