import flask
from insta485 import app
from insta485.model import grab_db
import pathlib
import uuid
import insta485
from flask import Flask, request
import hashlib
import os

#most of these are basically post requests
"""
/uploads/<filename>
/likes/?target=URL
/comments/?target=URL
/posts/?target=URL
/following/?target=URL

what we're targetting
"""

#since its a very bad idea to store passwords in a string format, we should encrypt it into the database so its impossible to figure out whether or not our password the user sends matches the encrypted format we stored in the database 
def generate_password_hash(password: str) -> str:
  algorithm = 'sha256'
  salt = uuid.uuid4().hex
  hash_obj = hashlib.new(algorithm) #how we hash passwords

  hash_input = (salt + password).encode('utf-8')
  hash_obj.update(hash_input) #input the salt and password 
  password_hash = hash_obj.hexdigest() #now the code will become completely new and incomprehensible to reverse
  # '031edd7d41651593c5fe5c006fa5752b37fddff7bc4e843aa6af0c950f4b9406'

  #formate: Algorithm$salt$hash
  return f"{algorithm}${salt}${password_hash}"


#password provided will be whatever our user inputs for their password
def verify_password(stored_password_format: str, password_provided: str) -> bool:
  """varifies password against a stored algorithm$hash string"""
  if not stored_password_format or '$' not in stored_password_format:
    return False

  extract_password = stored_password_format.split("$")
  #extract_password = ['sha256', uuid.uuid4().hex, '651593c5fe5c006fa5752']

  hash_obj = hashlib.new(extract_password[0]) #insert the algorithm
  hash_input = (extract_password[1] + password_provided).encode('utf-8')
  hash_obj.update(hash_input)

  if hash_obj.hexdigest() == extract_password[2]: #check if our hash_obj hexdigest is = to the password that we provided
    return True
  else:
    return False

################################# Password hashing ^^^ ########################


#Uploading folders and files, this handles serving dynamic files like profile pictures and post uploads
@app.route('/uploads/<filename>', methods=['GET']) #serving files must be a GET request
def get_upload(filename):
    """Serve uploaded images securely."""
    #Check if user is logged in 
    if 'username' not in flask.session:
        flask.abort(403) #username not logged in redirects them to login page
    filepath = insta485.app.config['UPLOAD_FOLDER'] / filename #grab a file or whatever, make sure its like acceptable (png, jpeg, etc)
    if not filepath.is_file():
        flask.abort(404)
    return flask.send_from_directory(app.config['UPLOAD_FOLDER'], filename)

############################### Upload files ^^^ ###################################


@app.route('/comments/', methods=['POST'])
def update_comments():
  #HANDLE comment creation and deletion
  if 'username' not in flask.session:
    flask.abort(403)

  logname = flask.session['username']

  operation = flask.request.form.get('operation') #operation is what we get from the HTML
  """
  <input type="hidden" name="operation" value="like"/> for example lol
  whenever we say create or delete a comment, the value should tell us what action we're doing
  and all of that will be stored inside of a name lol
  """
  target = flask.request.args.get('target', '/') #web request parameter

  connection = grab_db()
  cur = connection.cursor()

  if operation == 'create':
    whatpost = flask.request.form.get("postid")
    whattext = flask.request.form.get("text")

    cur.execute("INSERT INTO comments (owner, postid, text) VALUES (%s, %s, %s)", (logname, whatpost, whattext))
    connection.commit()

  if operation == 'delete':
    commentid = flask.request.form.get("commentid")

    cur.execute("DELETE FROM comments WHERE commentid = %s and OWNER = %s", (commentid, logname))
    connection.commit()

  return flask.redirect(target) #update page with new data (gonna have to reload first)


#LIKING A POST 
@app.route('/likes/', methods=['POST'])
def update_likes():

  if 'username' not in flask.session:
    return flask.redirect('/accounts/login/')

  logname = flask.session['username']
  operation = flask.request.form.get('operation') #find create or delete
  target = flask.request.args.get('target', '/')
  postid = flask.request.form.get("postid")

  connection = grab_db()
  cur = connection.cursor() #select whats in database

  if operation == 'like':
    cur.execute("INSERT INTO likes (owner, postid) VALUES (%s, %s)", (logname, postid,))

  if operation == 'unlike':
    cur.execute("DELETE FROM likes WHERE owner = %s AND postid = %s", (logname, postid,))

  connection.commit()

  return flask.redirect(target) #after liking should redirect us


#CREATE OR DELETE POST
@app.route('/posts/', methods=['POST'])
def update_posts():
  if 'username' not in flask.session:
    return flask.redirect('/accounts/login/')

  logname = flask.session['username']
  operation = flask.request.form.get('operation') #create or delete posts
  target = flask.request.args.get('target', f'/users/{logname}/')

  connection = grab_db()
  cur = connection.cursor()

  if operation == 'create':
    fileobj = flask.request.files["file"]
  
    # Unpack flask object
    filename = fileobj.filename

    # Compute base name (filename without directory).  We use a UUID to avoid
    # clashes with existing files, and ensure that the name is compatible with the
    # filesystem. For best practive, we ensure uniform file extensions (e.g.
    # lowercase).
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(filename).suffix.lower()
    uuid_basename = f"{stem}{suffix}"

    # Save to disk
    path = pathlib.Path(insta485.app.config["UPLOAD_FOLDER"])/uuid_basename
    fileobj.save(path)

    cur.execute("INSERT INTO posts (owner, filename) VALUES (%s, %s)", (logname, uuid_basename))
    connection.commit()

  if operation == 'delete':

    #Get postid from form data
    postid = flask.request.form.get('postid')

    #verify we can find the filename before deletion
    cur.execute("SELECT owner, filename FROM posts WHERE postid = %s", (postid,))
    post = cur.fetchone() #grab the one post we've selected

    if not post or logname != post['owner']:
      flask.abort(403)
    else:
      img_path = pathlib.Path(insta485.app.config["UPLOAD_FOLDER"])/post['filename']
      if img_path.exists(): #if we find the image we delete it from the system
        os.remove(img_path)

      cur.execute("DELETE FROM posts WHERE postid = %s and filename = %s and OWNER = %s", (postid, post['filename'],logname))
      connection.commit()

  return flask.redirect(target)


#FOLLOWING OR NOT
  #log in with logname
  #find create or delete operation

  #connect database
  #cursor in database
@app.route('/following/', methods=["POST"])
def update_following():
  if 'username' not in flask.session:
    return flask.redirect('/accounts/login/')

  logname = flask.session['username']
  username = flask.request.form.get('username')
  operation = flask.request.form.get('operation') #follow or unfollow
  target = flask.request.args.get('target', '/')

  connection = grab_db()
  cur = connection.cursor()

  cur.execute("SELECT 1 FROM following WHERE follower = %s AND followee = %s", (logname, username,))
  is_following = bool(cur.fetchone())

  if operation == 'follow':
    if not is_following:
      cur.execute("INSERT INTO following (follower, followee) VALUES (%s, %s)", (logname, username,))
    else:
      flask.abort(409)

  if operation == 'unfollow':
    if is_following: #if the user is following, we use WHERE to locate the query
      cur.execute("DELETE FROM following WHERE follower = %s AND followee = %s", (logname, username,))
    else:
      flask.abort(409)

  connection.commit()
  return flask.redirect(target)



@app.route('/accounts/', methods=['POST'])
def handle_account_actions():
  #get operation & target redirect URL from post request
  operation = flask.request.form.get('operation')
  target = flask.request.args.get('target', '/')
  connect_db = grab_db()
  current = connect_db.cursor()


  if operation == 'login': #grab login input
    username = flask.request.form.get('username')
    password = flask.request.form.get('password')

    if not username or not password:
      flask.abort(400)

    
    current  = connect_db.cursor()

    current.execute("SELECT password FROM users WHERE username = %s", (username,))
    #aye tell our database to grab our passwords for cryin out loud and compare it
    user = current.fetchone() #grab the next single row of the set



    if not user or not verify_password(user['password'], password): #compare user password to database password
      flask.abort(403) #if password no match we throw error ooguh

    #Set session variable to login the user
    flask.session['username'] = username 
    return flask.redirect(target)
  
  elif operation == 'logout':
    flask.session.clear() #removes user being logged in
    return flask.redirect(flask.url_for('show_login'))

  elif operation == 'create':
    create_account(connect_db)
    return flask.redirect(target)

  elif operation == 'delete':
    if 'username' not in flask.session:
      flask.abort(403)
    delete_account(connect_db)
    return flask.redirect(flask.url_for('show_login'))

  elif operation == 'edit_account':
    if 'username' not in flask.session:
      flask.abort(403)
    logname = flask.session['username']
    edit_account(logname, connect_db)
    return flask.redirect(flask.url_for('user_profile', username=logname))

  elif operation == 'update_password':
    if 'username' not in flask.session:
      flask.abort(403)
    logname = flask.session['username']
    password_update(logname, connect_db)
    return flask.redirect(target)

  #Flask.abort(400)

def create_account(connect_db):
  username = flask.request.form.get('username')
  password = flask.request.form.get('password')
  fullname = flask.request.form.get('fullname')
  file_object = flask.request.files.get("file")
  email = flask.request.form.get("email")

  filename = file_object.filename
  if filename is None or not password or not username or not email:
    flask.abort(400)

  #before we can add password into our database we should hash it first
  new_protected_password = generate_password_hash(password)

  # Compute base name (filename without directory).  We use a UUID to avoid
  # clashes with existing files, and ensure that the name is compatible with the
  # filesystem. For best practive, we ensure uniform file extensions (e.g.
  # lowercase).
  stem = uuid.uuid4().hex
  suffix = pathlib.Path(filename).suffix.lower()
  uuid_basename = f"{stem}{suffix}"

  # Save to disk
  path = pathlib.Path(insta485.app.config["UPLOAD_FOLDER"])/uuid_basename
  file_object.save(path)

  #If user tries creating an account with existing username
  cur = connect_db.cursor()

  cur.execute(
    "SELECT * FROM users WHERE username = %s", (username, )
  )

  if cur.fetchone() is not None: #if username does exist and its overlapping with the users input for username
    flask.abort(409)

  cur.execute("INSERT INTO users (username, fullname, email, filename, password) VALUES (%s, %s, %s, %s, %s)", (username, fullname, email, uuid_basename, new_protected_password))
  connect_db.commit()

  flask.session['username'] = username #login now

def delete_account(connect_db):
  username = flask.session['username']
  cur = connect_db.cursor()

  grab_all_users_post = cur.execute(
    "SELECT filename FROM posts WHERE owner = %s", (username, )
  )

  all_posts = grab_all_users_post.fetchall() #find every post related to the user
  for each_post in all_posts:
    old_uuid_basename = each_post['filename'] #get the post img
    img_path = pathlib.Path(insta485.app.config["UPLOAD_FOLDER"])/old_uuid_basename

    if img_path.exists(): #if we find the file associated with account remove
      os.remove(img_path) #navigate to the file and remove it
  cur.execute("DELETE FROM users WHERE username = %s", (username,))
  connect_db.commit()
  flask.session.clear() #clear username session after success

def edit_account(logname, connect_db):
  fullname = flask.request.form.get('fullname')
  email = flask.request.form.get('email')
  file_object = flask.request.files.get('file')
  target = flask.request.args.get('target', f'/users/{logname}/')

  #unlock file object
  cur = connect_db.cursor()
  if not file_object: #edit only fullname and email

    cur.execute("UPDATE users SET fullname = %s, email = %s WHERE username = %s", (fullname, email, logname))
  else:
    filename = file_object.filename

    #remove old file
    cur.execute("SELECT * FROM users WHERE username = %s", (logname, )) #find the file from username
    old_uuid_basename = cur.fetchone()['filename'] #get file
    old_img_path = pathlib.Path(insta485.app.config["UPLOAD_FOLDER"])/old_uuid_basename
    if old_img_path.exists():
      os.remove(old_img_path) #removefile

    stem = uuid.uuid4().hex #encrypt our file so if someone uploads the same filename we it doesnt overlap
    suffix = pathlib.Path(filename).suffix.lower()
    uuid_basename = f"{stem}{suffix}"

    # Save to disk
    path = pathlib.Path(insta485.app.config["UPLOAD_FOLDER"])/uuid_basename
    file_object.save(path)

    #execute object now within user, with new file
    cur.execute("UPDATE users SET fullname = %s, email = %s, filename = %s WHERE username = %s", (fullname, email, uuid_basename, logname))

  connect_db.commit()
  return flask.redirect(target)

def password_update(logname, connect_db):
  old_password = flask.request.form.get('password')
  new_password = flask.request.form.get('new_password1')
  password_again = flask.request.form.get('new_password2')
  cur = connect_db.cursor()

  #passwords must match
  if new_password != password_again:
    flask.abort(401)
  #Get our current right password
  cur.execute("SELECT * FROM users WHERE username = %s", (logname, ))
  users_password = cur.fetchone()

  #verify password with users password, and our old password
  if users_password and verify_password(users_password['password'], old_password):
    new_password_hashed = generate_password_hash(password_again)
    #find username and set their password again
    cur.execute("UPDATE users SET password = %s WHERE username = %s", (new_password_hashed, logname))
    connect_db.commit()
  else:
    flask.abort(403) #passwords do not match

  

    