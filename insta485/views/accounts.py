#/accounts/?target=URL
#/accounts/create/, /accounts/edit/, /accounts/password/, /accounts/delete/, /accounts/edit, /accounts/password/

import flask
from flask import Flask, request
import insta485
from insta485 import app
from insta485.model import grab_db



@app.route("/accounts/login/", methods=['GET'])
def show_login():
  if 'username' in flask.session:
    return flask.redirect(flask.url_for('show_index'))
  else:
    return flask.render_template("login.html") #redirect to our login html page

@app.route("/accounts/create/", methods=['GET'])
def create_account():
  if 'username' in flask.session:
    return flask.redirect(flask.url_for('edit_account'))
  else:
    return flask.render_template("create.html") #redirect to our login html page


@app.route("/accounts/delete/", methods=['GET'])
def delete_account():
  if 'username' not in flask.session:
    return flask.redirect(flask.url_for('show_login'))
  logname = flask.session["username"]
  context = {"logname": logname, "curr_path": request.path}
  return flask.render_template("delete.html", **context) #redirect to delete HTML

@app.route("/accounts/edit/", methods=["GET"])
def edit_account():
  if 'username' not in flask.session:
    return flask.redirect(flask.url_for('show_login'))

  logname = flask.session["username"]

  connection = grab_db()
  cur = connection.cursor()

  cur.execute(
    "SELECT * FROM users WHERE username = %s", (logname,)
  )
  user = cur.fetchone() #grab username ofc, just a single username from the users table

  context = {"logname": logname, 
             "username": logname,
             "photo": user['filename'], 
             "fullname": user['fullname'],
             "email": user['email'], 
             "curr_path": request.path}
  
  return flask.render_template("edit.html", **context)

@app.route("/accounts/password/", methods=["GET"])
def edit_password():
  if 'username' not in flask.session:
    return flask.redirect(flask.url_for('show_login'))

  logname = flask.session["username"] #grab username as usual
  context = {"logname": logname, "curr_path": request.path}
  return flask.render_template("password.html", **context) #redirect to changing passwords