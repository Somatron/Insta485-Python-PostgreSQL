import hashlib
import uuid
from flask import Flask
import sqlite3
import psycopg

app = Flask(__name__)
app.secret_key = "super_secret_key"

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

def grab_db():
  "Helper to aquire database connection"
  conn_params = {
    "dbname": 'postgres',
    "user": 'postgres',
    "password": '1D0ll@rDVD',
    "host": 'localhost',
    "port": '5432'
  }


@app.route("/accounts/login/", methods=['GET'])
def show_login():
  if 'username' in Flask.session:
    return Flask.redirect(Flask.url_for('show_index'))
  else:
    return Flask.render_template("login.html") #redirect to our login html page

@app.route('/accounts/', methods=['POST'])
def handle_account_actions():
  #get operation & target redirect URL from post request
  operation = Flask.request.form.get('operation')
  target = Flask.request.args.get('target', '/')

  if operation == 'login': #grab login input
    username = Flask.request.form.get('username')
    password = Flask.request.form.get('password')

    if not username or not password:
      Flask.abort(400)

    db = grab_db()
    current  = db.execute("SELECT password FROM users WHERE username = ?", (username,))
    #aye tell our database to grab our passwords for cryin out loud and compare it
    user = current.fetchone() #grab the next single row of the set

    if not user or not verify_password(user['password'], current): #compare user password to database password
      Flask.abort(400) #if password no match we throw error ooguh

    #Set session variable to login the user
    Flask.session['username'] = username 
    return Flask.redirect(target)

  elif operation == 'logout':
    Flask.session.clear() #removes user being logged in
    return Flask.redirect(Flask.url_for('show_login'))

  Flask.abort(400)




    