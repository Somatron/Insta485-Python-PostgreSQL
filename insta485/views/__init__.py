from flask import Flask

app = Flask(__name__)

app.config.from_object('insta485.config') #grab from our insta485 folder configs

#Import views
import insta485.model
from insta485.views.index import show_index
from insta485.views.accounts import *  # or your specific view functions
from insta485.views.posts import *