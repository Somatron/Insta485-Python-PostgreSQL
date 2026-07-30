#/accounts/?target=URL
#/accounts/create/, /accounts/edit/, /accounts/password/, /accounts/delete/, /accounts/edit, /accounts/password/

import uuid
from flask import Flask, request
import sqlite3
import psycopg

app = Flask(__name__)
app.secret_key = "super_secret_key"

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

@app.route("/accounts/create/", methods=['POST'])
def create_account():
  if 'username' in Flask.session:
    return Flask.redirect(Flask.url_for('show_edit'))
  else:
    return Flask.render_template("login.html") #redirect to our login html page


@app.route("/accounts/delete/", methods=['POST'])
def delete_account():
  if 'username' not in Flask.session:
    return Flask.redirect(Flask.url_for('show_login'))
  logname = Flask.session["username"]
  context = {"logname": logname}
  return Flask.render_template("delete.html", **context) #redirect to delete HTML

@app.route("/accounts/edit")
def edit_account():
  if 'username' not in Flask.session:
    return Flask.redirect(Flask.url_for('show_login'))

  logname = Flask.session["username"]

  connection = grab_db()
  cur = connection.cursor()

  cur.execute(
    "SELECT users WHERE username = %s", (logname,)
  )
  user = cur.fetchall()[0] #grab username ofc

  context = {"logname": logname, "username": logname,
             "photo": user['filename'], "fullname": user['fullname'],
             "email": user['email'], "curr_path": request.path}
  
  return Flask.render_template("edit.html", **context)

@app.route("/accounts/password/")
def edit_password():
  if 'username' not in Flask.session:
    return Flask.redirect(Flask.url_for('show_login'))

  logname = Flask.session["username"] #grab username as usual
  context = {"password": logname}
  return Flask.render_template("password.html", **context) #redirect to changing passwords