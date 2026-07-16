import json
import uuid
from datetime import timedelta
from django.utils import timezone
from users.models import SessionStorage

COOKIE_NAME = 'my_custom_session_id'
SESSION_AGE = timedelta(minutes=30)

class SessionStore(dict):
    """
    A dictionary that has the necessary methods to be compatible with django.contrib.auth.
    """

    def __init__(self, session_key=None):
        super().__init__()
        self.session_key = session_key
        self.modified = False

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.modified = True

    def __delitem__(self, key):
        super().__delitem__(key)
        self.modified = True