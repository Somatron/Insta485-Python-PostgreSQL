"""
Insta485 index (main) view.

URLs include:
/explore yay/
/users/<user_url_slug>/    users -- if im user edit, if user follows target: following    
/users/<user_url_slug>/followers/      determine if logged in user is following  
/users/<user_url_slug>/following/      only display html if user following
/posts/<postid_url_slug>/      kinda the same as get index.html
"""
import flask
import insta485
from insta485 import app
from insta485.model import grab_db
import arrow
from flask import request
  

#MAIN FEED
@insta485.app.route('/')
def show_index():
    """Display / route."""

    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))

    connection = grab_db()
    # Connect to database
    logname = flask.session['username'] #get username
    #2. Open cursor to execute query
    cur = connection.cursor()

    query = """
        SELECT posts.postid, posts.filename AS img_friend, users.filename AS owner_img_url, posts.owner, posts.created AS timestamp FROM posts INNER JOIN users ON posts.owner = users.username WHERE posts.owner = %s OR posts.owner IN (SELECT followee FROM following WHERE follower = %s)
        ORDER BY posts.postid DESC;
    """
    cur.execute(query, (logname, logname))
    posts = cur.fetchall() #get all posts
    #clean up cursor when done
    for post in posts:
        #humanize means "an hour ago"/"in 3 days"
        post["timestamp"] = arrow.get(str(post["timestamp"])).humanize()

        #fetch comments for post, we dont need postid since we already have it
        cur.execute("SELECT commentid, owner, text FROM comments WHERE postid = %s ORDER BY commentid ASC", (post['postid'],)) #place these comments in appropriate postid
        post['comments'] = cur.fetchall() #shows us whoever is logged in

        cur.execute("SELECT filename FROM users WHERE username = %s", (logname, ))
        user_profile_pic = cur.fetchall()[0]["filename"]

        #check if logged in user liked the post
        cur.execute("SELECT 1 FROM likes WHERE owner = %s AND postid = %s", (logname, post['postid'])) #whoever is logged in see if they liked the post or not
        post['user_liked'] = cur.fetchone() is not None #see if like actually exists

        #Count total likes for each post in the feed
        cur.execute("SELECT COUNT(*) AS total_likes FROM likes WHERE postid = %s", (post['postid'],))
        post['likes'] = cur.fetchone()['total_likes']


    context = {"logname": logname, 
               "posts": posts, 
               "user_profile_pic": user_profile_pic,
               "curr_path": request.path} #pass this to render into HTML for jinja to render 
    return flask.render_template("index.html", **context)


#INDIVIDUAL POST
@insta485.app.route("/posts/<postid>/", methods=['GET'])
def show_individual_post(postid):
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))

    connection = grab_db()
    logname = flask.session['username']

    #verify users posdt
    query = """
    SELECT posts.postid, posts.filename as img_friend, posts.owner, posts.created AS timestamp, users.filename AS owner_img_url FROM posts INNER JOIN users ON posts.owner=users.username WHERE posts.postid = %s
    """
    cur = connection.cursor()
    cur.execute(query, (postid,)) #dont forget to pass in as a tuple for databases to organize data

    post_check = cur.fetchall() #grab current post we're on
    if not post_check:
        flask.abort(404)
    post = post_check[0]


    post["timestamp"] = arrow.get(str(post["timestamp"])).humanize() #puts into 2 days ago format

    #Get comments
    cur.execute("SELECT commentid, owner, text FROM comments WHERE postid = %s ORDER BY commentid ASC", (postid,))
    comments = cur.fetchall() #grab all comments assigned to the post number

    cur.execute("SELECT COUNT(commentid) as your_comment FROM comments WHERE postid = %s AND owner = %s", (postid, logname, ))
    post["logname_comment"] = cur.fetchall()[0]["your_comment"]

    #grab like counts
    cur.execute("SELECT COUNT(*) AS likes FROM likes WHERE postid = %s", (postid, ))
    all_likes = cur.fetchone()["likes"] #grab the likes from the post we're at

    #Find likes owners, differentiate whether the logged in user liked the post or not
    cur.execute("SELECT COUNT(*) AS unique_like FROM likes WHERE postid = %s AND owner = %s", (postid, logname, ))
    post["like_button"] = cur.fetchone()["unique_like"] #see if owner has liked the post or not, determines the like button

    cur.execute("SELECT filename FROM users WHERE username = %s", (logname, ))
    user_pfp_pic = cur.fetchall()[0]["filename"]

    context = {"logname": logname, 
               "post_likes": all_likes, 
               "likes": post["like_button"], 
               "post_comments": comments, 
               "owner_img_url": post["owner_img_url"], 
               "post_image": post["img_friend"], 
               "owner": post["owner"], 
               "user_pfp_pic": user_pfp_pic,
               "timestamp": post["timestamp"], 
               "is_my_comment": post["logname_comment"], 
               "postid": postid, 
               "curr_path": request.path}
    return flask.render_template("post.html", **context)

#USER PAGE
@insta485.app.route("/users/<username>/", methods=['GET'])
def user_profile(username): #get the user profile into our parameter 
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))

    connection = grab_db()
    logname = flask.session['username']
    cur = connection.cursor()

    cur.execute( #check if username exists in database, if not go to 404
        "SELECT * FROM users WHERE username = %s", (username, ))
    if cur.fetchone() is None:
        flask.abort(404)


    cur.execute(
        "SELECT * FROM following WHERE follower = %s AND followee = %s", (logname, username, )
    )
    logname_follows_username = bool(cur.fetchone()) #grabs a true and false statement to make sure if the user
    #is following the user or not

    #Get all of the total posts of <username> as a count
    cur.execute( #get all of the userposts that the username played
        "SELECT COUNT(postid) AS count FROM posts WHERE owner = %s", (username,)
    )
    users_post_count = cur.fetchall()[0]["count"] #to display as 4 posts or how many posts they have


    #Get the fullname of username
    cur.execute("SELECT fullname FROM users WHERE username = %s", (username, ))
    get_user_details = cur.fetchall()[0]["fullname"] #get the users full name

    cur.execute("SELECT filename FROM users WHERE username = %s", (username, ))
    user_profile_pic = cur.fetchall()[0]["filename"]

    #get followers and following
    cur.execute("SELECT COUNT(*) AS count FROM following WHERE follower = %s", (username, ))
    followers = cur.fetchall()[0]["count"]
    cur.execute("SELECT COUNT(followee) AS count FROM following WHERE followee = %s", (username, ))
    following = cur.fetchall()[0]["count"]

    cur.execute("SELECT postid, filename AS img_url FROM posts WHERE owner = %s", (username, ))
    image_posts = cur.fetchall()
    #We have all of the nessessary details needed for our user
    context = {"logname": logname, 
               "username": username, 
               "fullname": get_user_details, 
               "posts": users_post_count, 
               "following": following, 
               "followers": followers, 
               "user_profile_pic": user_profile_pic,
               "logname_follows_username": logname_follows_username, 
               "image_posts": image_posts, 
               "curr_path": request.path}
    return flask.render_template("user.html", **context)

#FOLLOWERS
@insta485.app.route("/users/<username>/followers/", methods=['GET'])
def user_followers(username):
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))

    logname = flask.session['username']

    connection = grab_db()
    cur = connection.cursor()

    #if someone tries to access a user_url_slug that does not exist in the database, then abort(404).
    cur.execute( #check if username exists in database, if not go to 404
    "SELECT * FROM users WHERE username = %s", (username, )
    )
    if cur.fetchone() is None:
        flask.abort(404)

    #find if <username> follows each follower
    cur.execute( #chooses user file, and username, connects users table to the following table by matching the users main profile name with the person being followed
        #WHERE it filters the list of the people followed by the target user
        "SELECT users.filename as user_img_url, users.username FROM users INNER JOIN following ON users.username=following.follower WHERE following.followee = %s", (username, )
    )
    user_followers = cur.fetchall() #get all of the users and the relationship to the logged in user

    for follower in user_followers: #navigate for each user
        cur.execute("SELECT * FROM following WHERE follower = %s AND followee = %s", (logname, follower["username"], )) #find the relationship of the user
        follower["logname_follows_username"] = bool(cur.fetchone()) #true or false


    #dictionary
    context = {"logname": logname, 
               "username": username, 
               "user_followers": user_followers, 
               "curr_path": request.path}
    return flask.render_template("followers.html", **context)


#FOLLOWING
@insta485.app.route("/users/<username>/following/", methods=['GET'])
def user_following(username):
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))

    logname = flask.session['username']
    connection = grab_db()
    cur = connection.cursor()

    #make sure the user_url_slug exists ofc
    cur.execute(
        "SELECT * FROM users WHERE username = %s", (username, )
    )
    if cur.fetchone() is None:
        flask.abort(404)

    cur.execute( #gonna grab our relationship graph
        "SELECT users.filename AS user_img_url, users.username FROM users INNER JOIN following ON users.username=following.followee WHERE following.follower = %s", (username,)
    ) #CHECK the person on the following page and see if the logged in user A is following this person B, AND THEN compare the usernames relationship with the person B

    user_followings = cur.fetchall()

    for followee in user_followings:
        cur.execute("SELECT * FROM following WHERE follower = %s AND followee = %s", (logname, followee["username"], )) #usernames following person, god this logic is a nightmare
        followee["logname_follows_username"] = bool(cur.fetchone()) #see if this is true or not

    context = {"logname": logname, 
               "username": username, 
               "user_followings": user_followings,
               "curr_path": request.path}
    return flask.render_template("following.html", **context)


#EXPLORE PAGE
@insta485.app.route("/explore/", methods=['GET'])
def explore():
    if 'username' not in flask.session:
        return flask.redirect(flask.url_for('show_login'))

    logname = flask.session['username']
    connection = grab_db()
    cur = connection.cursor()


    cur.execute( #except helps us display users that the logged in user is not following, its basically saying EXCEPT the users that the logged in user is already following
        "SELECT username, filename AS user_img_url FROM users WHERE username != %s AND username NOT IN (SELECT followee FROM following WHERE follower = %s)", (logname, logname)
    )
    not_following = cur.fetchall()

    context = {"logname": logname, 
               "not_following": not_following, 
               "curr_path": request.path}
    return flask.render_template("explore.html", **context)

