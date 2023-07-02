from django.urls import path
from django.conf import settings
from django.conf.urls.static import static


from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register, name='register'),
    path('logout', views.logout_view, name='logout'),
    path('login', views.login_view, name='login'),
    path('loaddata', views.loadData, name='loadData'),
    path('newpost/<str:postType>', views.newPost, name='newpost'),
    path('post/<int:postID>', views.post, name='post'),
    path('tag/<str:tagSlug>', views.tag, name='tag'),
    path('user/<str:username>/gallery', views.userGallery, name='userGallery'),
    path('user/<str:username>/writing', views.userWriting, name='userWriting'),
    path('user/<str:username>/blogs', views.userBlogs, name='userBlogs'),
    path('user/<str:username>/likes', views.userLikes, name='userLikes'),
    path('user/<str:username>/following', views.userFollowing, name='userFollowing'),
    path('user/<str:username>/followers', views.userFollowers, name='userFollowers'),
    path('user/<str:username>', views.user, name='user'),
    path('deletePost/<int:postID>', views.deletePost, name='deletePost'),
    path('deleteComment/<int:commentID>', views.deleteComment, name='deleteComment'),
    path('editUser/<str:username>', views.editUser, name='editUser'),

    # API Routes
    path('follow/<str:username>', views.follow, name='follow'),
    path('unfollow/<str:username>', views.unfollow, name='unfollow'),
    path('unlike/<int:postID>', views.unlike, name='unlike'),
    path('like/<int:postID>', views.like, name='like')
]