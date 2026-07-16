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

    def cycle_key(self):
        """After login, the session key is changed but the data remains (preventing session persistence)."""
        data = dict(self)
        self.flush()
        self.update(data)
        self.modified = True

    def flush(self):
        """Called when logging out: all data is cleared and the key is invalidated."""
        self.clear()
        if self.session_key:
            SessionStorage.objects.filter(session_key=self.session_key).delete()
        self.session_key = None
        self.modified = True

class SimpleCookieSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        session_key = request.COOKIES.get(COOKIE_NAME)
        session = SessionStore(session_key)
