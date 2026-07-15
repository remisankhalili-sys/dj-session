import json
import uuid
from django.core import exceptions
from django.conf import settings
from users.models import SessionStorage 


class SimpleCookieSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.cookie_name = 'my_custom_session_id' 
    """
    A custom middleware that stores session data in a signed cookie.
    This prevents users from tampering with the session data.
    """


    def __call__(self, request):
        
        session_id = request.COOKIES.get(self.cookie_name)
        request.session = {} 

        if session_id:
            try:
              
                storage = SessionStorage.objects.get(session_key=session_id)
                request.session = json.loads(storage.session_data)
                
                request._session_id = session_id 
            except SessionStorage.DoesNotExist:
               
                request._session_id = None
            except json.JSONDecodeError:
                request._session_id = None
        else:
            request._session_id = None

        response = self.get_response(request)

        if request.session:
        #If the session is new, generate a random ID.   
            if not request._session_id:
                new_id = str(uuid.uuid4())
                request._session_id = new_id