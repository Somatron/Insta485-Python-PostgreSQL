"""Insta485 package initializer."""
import flask

# app is a single object used by all the code modules in this package
app = flask.Flask(__name__)  # pylint: disable=invalid-name

# Read settings from config module (insta485/config.py)
app.config.from_object('insta485.config')

# Overlay settings read from a Python file whose path is set in the environment
# variable INSTA485_SETTINGS. Setting this environment variable is optional.
# Docs: http://flask.pocoo.org/docs/latest/config/
#
# EXAMPLE:
# $ export INSTA485_SETTINGS=secret_key_config.py
app.config.from_envvar('INSTA485_SETTINGS', silent=True)

# Tell our app about views and model.  This is dangerously close to a
# circular import, which is naughty, but Flask was designed that way.
# (Reference http://flask.pocoo.org/docs/patterns/packages/)  We're
# going to tell pylint and pycodestyle to ignore this coding style violation.

import insta485.views #yk to import our index
import insta485.model
from insta485.views.index import show_index, show_individual_post, user_profile, user_followers, user_following, explore
from insta485.views.accounts import show_login, create_account, delete_account, edit_account, edit_password  # or your specific view functions
from insta485.views.posts import update_comments, update_likes, update_posts, update_following, handle_account_actions