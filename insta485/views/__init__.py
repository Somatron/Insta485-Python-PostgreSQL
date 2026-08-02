from flask import Flask

app = Flask(__name__)

app.config.from_object('insta485.config') #grab from our insta485 folder configs
app.config.from_envvar('INSTA485_SETTINGS', silent=True)

#Import views
import insta485.views
import insta485.model
from insta485.views.index import show_index, show_individual_post, user_profile, user_followers, user_following, explore
from insta485.views.accounts import show_login, create_account, delete_account, edit_account, edit_password  # or your specific view functions
from insta485.views.posts import update_comments, update_likes, update_posts, update_following, handle_account_actions