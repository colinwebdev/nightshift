import os
from django.conf import settings
import urllib.request
from random import randint, choice
import csv
import ssl
import cairosvg
from urllib.error import HTTPError
from django.core.exceptions import ObjectDoesNotExist
import string

from .models import *

dataFolder = os.path.join(settings.BASE_DIR, 'gallery/data')

def loadCSV(file):
    
    csvData = []
    csvFile = os.path.join(dataFolder, file)
    with open(csvFile, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            entry = {}
            for col in row:
                entry[col] = row[col]
                csvData.append(entry)
    return csvData

def makeUsers(num):
    addedRows = []
    if num == 0:
        num = randint(10, 50)
    print("processing")
    userData = loadCSV('users.csv')
    taglines = loadCSV('titles.csv')
    bios = loadCSV('posttext.csv')
    userLast = len(userData) - 1
    tagLast = len(taglines) - 1
    bioLast = len(bios) - 1
    diceBear = 'https://avatars.dicebear.com/api/'
    styles = ['adventurer', 'adventurer-neutral', 'avataaars', 'big-ears',
              'big-ears-neutral', 'big-smile', 'bottts', 'croodles', 'croodles-neutral', 'micah', 'miniavs', 'open-peeps']
    while len(addedRows) < num:
        username = userData[randint(0, userLast)]['username']
        try:
            userCheck = User.objects.get(username=username)
            continue
        except ObjectDoesNotExist:
            pass

        password = userData[randint(0, userLast)]['password']
        email = userData[randint(0, userLast)]['email']
        tagline = taglines[randint(0, tagLast)]['title']
        bio = bios[randint(0, bioLast)]['posttext']

        pronouns = ''
        whichPronoun = randint(0, 2)
        if whichPronoun == 0:
            pronouns = 'She/Her'
        elif whichPronoun == 1:
            pronouns = 'He/Him'
        else:
            pronouns = 'They/They'

        style = styles[randint(0, (len(styles) - 1))]
        background = ''
        seed = username
        for _ in range(3):
            hexnum = randint(0, 255)
            background += f'{hexnum:x}'
        url = diceBear + style + '/' + seed + '.svg?' + 'background=%23' + str(background)
        if (randint(1, 5) % 5 == 0):
            url += '&flip=true'
        
        try:
            user = User.objects.create_user(username, email, password)
            user.save()

            getUser = User.objects.get(username=username)

            userFolder = os.path.join('uploads', 'user_' + str(getUser.id))
            isExist = os.path.exists(userFolder)
            if not isExist:
                os.makedirs(userFolder)
                print("The new directory is created!")
            print(f'Getting avatar {url}')
            ssl._create_default_https_context = ssl._create_unverified_context
            fileName = os.path.join(userFolder, seed + '.png')
            cairosvg.svg2png(url=url, write_to=fileName)
            print(fileName)
            getUser.pronouns = pronouns
            getUser.title = tagline
            getUser.bio = bio
            getUser.avatar = os.path.join('user_' + str(getUser.id), seed + '.png')
            getUser.save()

            update = f'Username: {username}, Email: {email}, Pronouns: {pronouns}, Tagline: {tagline}, Bio: {bio}, Avatar: {getUser.avatar.url}'
            addedRows.append(update)
            print(update)
        except HTTPError:
            print('HTTPError')
            pass
    newData = [len(addedRows), addedRows]
    return newData

def makePosts(num, user, postType):
    addedRows = []
    users = ''
    if num == 0:
        num = randint(10, 50)
    if user == '':
        users = User.objects.all()
    dates = loadCSV('dates.csv')
    posttext = loadCSV('posttext.csv')
    titles = loadCSV('titles.csv')
    userlast = len(users) - 1
    datelast = len(dates) - 1
    textlast = len(posttext) - 1
    titleslast = len(titles) - 1

    while len(addedRows) < num:
        userID = ''
        if user == '':
            userID = users[randint(0, userlast)].id
        else:
            userID = User.objects.get(id=int(user)).id
        text = posttext[randint(0, textlast)]['posttext']
        title = titles[randint(0, titleslast)]['title']
        image = ''
        entry = ''
        if postType == 'gallery':
            image = getImage(userID)
            imagePath = os.path.join('user_' + str(userID), image)
            entry = Post(postType='image', user=User(id=userID), postTitle=title, postBody=text, image=imagePath)
        else:
            entry = Post(postType=postType, user=User(id=userID), postTitle=title, postBody=text)
        try:
            entry.save()
            entry = Post.objects.latest('timePosted')
        except:
            continue
        tags = ''
        numtags = randint(1, 15)
        tags = makeTags(numtags, entry.id)
        update = f'Title: {title}, PostType: {postType}, UserID: {userID}, Tags: {tags}, Image: {image}'
        addedRows.append(update)
        print(update)
    newdata = [len(addedRows), addedRows]
    return newdata

def getImage(userID):
    userFolder = os.path.join('uploads', 'user_' + str(userID))
    image = ''
    while image == '':
        randstring = ''
        for _ in range(randint(5, 15)):
            randstring += choice(string.ascii_letters)
        imgName = randstring + '.jpg'
        url = 'https://picsum.photos/id/'
        imgid = randint(0, 999)
        url += str(imgid) + '/'
        width = randint(500, 900)
        height = randint(500, 1000)
        url += str(width) + '/' + str(height)
        if (randint(0, 10) % 9) == 0:
            url += '?grayscale'
        print(f'getting image {url}')
        try:
            ssl._create_default_https_context = ssl._create_unverified_context
            urllib.request.urlretrieve(url, os.path.join(userFolder, imgName))
            image = imgName
            return image
        except:
            
            print('HTTPError')
            pass

def makeTags(num, postID):
    tags = loadCSV('tags.csv')
    userID = Post.objects.get(id=postID).user.id
    tagLast = len(tags) - 1
    postTags = ''
    while len(postTags) < num:
        tag = tags[randint(0, tagLast)]['text']
        slug = tag.strip().replace(' ', '-')
        postTags += tag + ", "
        tagID = ''
        try:
            tagID = Tag.objects.get(slug=slug)
        except ObjectDoesNotExist:
            addTag = Tag(tagText=tag, slug=slug, addedBy=User(id=userID))
            addTag.save()
            tagID = Tag.objects.latest('id')
        postTag = PostTags(post=Post(id=postID),tag=Tag(id=tagID.id))
        postTag.save()
    return postTags

def makeFollows(num):
    addedRows = []
    users = User.objects.all()
    if num == 0:
        num = randint(10, 50)
    userlast = len(users) - 1
    while len(addedRows) < num:
        source = users[randint(0, userlast)].id
        target = users[randint(0, userlast)].id
        if source != target:
            try: 
                Follows.objects.get(followSource=source, followTarget=target)
                continue
            except ObjectDoesNotExist:
                pass
            try:
                entry = Follows(followSource=User(id=source), followTarget=User(id=target))
                entry.save()
                update = f'User {source} followed {target}'
                addedRows.append(update)
            except:
                pass
    newData = [len(addedRows), addedRows]
    return newData

def makeLikes(num):
    addedRows = []
    users = User.objects.all()
    posts = Post.objects.all()
    if num == 0:
        num = randint(10,50)
    userLast = len(users) - 1
    postLast = len(posts) - 1
    while len(addedRows) < num:
        userID = users[randint(0, userLast)].id
        postID = posts[randint(0, postLast)].id
        try:
            check = Favorites.objects.filter(user=userID, post=postID)
        except ObjectDoesNotExist:
            pass
        try:
            entry = Favorites(user=User(id=userID), post=Post(id=postID))
            entry.save()
        except:
            continue
        update = f'Userid: {userID} liked {postID}'
        addedRows.append(update)
        print(update)
    newData = [len(addedRows), addedRows]
    return newData

def makeComments(num, userID):
    addedRows = []
    users = ''
    posts = Post.objects.all()
    if num == 0:
        num = randint(10,50)
    if userID == '':
        users = User.objects.all()
    text = loadCSV('sharecomments.csv')
    userLast = len(users) - 1
    postLast = len(posts) - 1
    textLast = len(text) - 1
    while len(addedRows) < num:
        userID = users[randint(0, userLast)].id
        postID = posts[randint(0, postLast)].id
        comment = text[randint(0, textLast)]['commenttext']
        try:
            entry = Comment(post=Post(id=postID), user=User(id=userID), text=comment)
            entry.save()
        except:
            pass
        update = f'UserID: {userID} liked: {postID}, comment: {comment}'
        addedRows.append(update)
        print(update)
    newData = [len(addedRows), addedRows]
    return newData

def makeProfileComments(num, userID):
    addedRows = []
    users = ''
    if num == 0:
        num = randint(10,50)
    if userID == '':
        users = User.objects.all()
    text = loadCSV('sharecomments.csv')
    userLast = len(users) - 1
    textLast = len(text) - 1
    while len(addedRows) < num:
        sourceID = users[randint(0, userLast)].id
        if userID == '':
            userID = users[randint(0, userLast)].id
        comment = text[randint(0, textLast)]['commenttext']
        try:
            entry = ProfileComment(profile=User(id=userID), commenter=User(id=sourceID), text=comment)
            entry.save()
        except:
            pass
        update = f'UserID: {sourceID} Commented On: {userID}, comment: {comment}'
        addedRows.append(update)
        print(update)
    newData = [len(addedRows), addedRows]
    return newData