"""Insta485 development configuration."""


import pathlib
import os

#Where the project folder is
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Root of this application, useful if it doesn't occupy an entire domain
APPLICATION_ROOT = '/'

# Secret key for encrypting cookies
SECRET_KEY = b'FIXME SET WITH: $ python3 -c "import os; print(os.urandom(24))" '
SESSION_COOKIE_NAME = 'login'

# File Upload to var/uploads/
INSTA485_ROOT = pathlib.Path(__file__).resolve().parent.parent
UPLOAD_FOLDER = INSTA485_ROOT/'var'/'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

# Database file is
DATABASE_URI = os.environ.get('DATABASE_URL','postgresql://username:password@localhost:5432/insta485')

# Enable CSRF protection
WTF_CSRF_ENABLED = True
