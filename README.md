# Night Shift - CS50W Capstone

Night Shift is a gallery website inspired by the 2010's era DeviantArt. It allows users to post images and stories to their own galleries, and other users can comment on or favorite the works. Users also have the ability to make blog posts and comment on profiles. All large blocks of text (stories, blogs, etc) support the use of markdown for formatting. 

Mock up data was used to fill the site with content and make it appear as though there were more users. Any text based data was acquired through Mockaroo, post images were gathered from Picsum.photo and avatars were generated using avatars.dicebear.com

## Distinctiveness and Complexity

While this project does share some baseline features as presented in Project 4, I believe it is more than distinct enough to stand on its own. The focus for this project is for users to share their works and creations, rather than short thoughts, with 3 distinct post types, and the ability to tag their posts, with a strong focus on image based content. 

For complexity, every user has an avatar that is displayed along with every comment left and on every post made. The posts themselves each have a type assigned, a title, and tags associated. This requires both a tags model and a model that associates posts and tags together. Images that are uploaded--both as avatars or as posts--are processed and renamed to ensure they are unique, then stored in the user's folder. There are also models for saving favorited posts, user follows, post comments, and profile comments. The site's interface allows users to navigate and browse all of this, including browsing by tags and seeing what other users have liked. The site interface includes JavaScript based dropdowns for profile management and making posts. 

## The Files

- Data Folder
  - Contains the CSVs used to populate data across the site
- Templates Folder
  - asideBlogs.html - a template to be called any time site-wide blogs should be displayed (usually on the front page)
  - editUser.html - a form for editing a user's own profile
  - index.html - the home page
  - layout.html - the skeleton structure of all pages
  - loadData.html - an admin only page that allows the population of random data
  - nav.html - the bar above all content that allows for navigation
  - newPost.html - the forum that accepts user input for making new posts
  - profile.html - the landing page for user profiles
  - profileHead.html - the portion of the user profile that contains their bio
  - profileView.html - displays the content of each of the tabs on a user's page -- likes, follows, etc
  - register.html - the form that is called for registration
  - tag.html - the page used for browsing tags
- Uploads Folder
  - Contains one folder for each user to store the files and avatars they have uploaded
- Other files
  - loadData.py - The Django code for importing user data

## Additional Requirements to Run

Pillow
django-mardownify

## How to Run

The standard command of `python manage.py runserver` automatically allows you to access the site while logged out. From there, no additional commands are needed. You may browse the site. If you register an account you can make posts and edit your profile. 

## Additional Information 

All text and user names, aside from the one post made by me for the video, are randomly generated, so it will look like absolute gibberish if you're not expecting it. 