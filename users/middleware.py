import json
import uuid
from datetime import timedelta
from django.utils import timezone
from users.models import SessionStorage

COOKIE_NAME = 'my_custom_session_id'
SESSION_AGE = timedelta(minutes=30)

