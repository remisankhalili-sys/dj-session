import json
import uuid
from datetime import timedelta
from django.utils import timezone
from users.models import SessionStorage 


class SimpleCookieSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.cookie_name = 'my_custom_session_id'
        self.max_age = timedelta(minutes=30) 
    """
    A custom middleware that stores session data in a signed cookie.
    This prevents users from tampering with the session data.
    """


    def __call__(self, request):
        
        session_id = request.COOKIES.get(self.cookie_name)
        request.session = {} 
        request._session_id = session_id

        if session_id:
            try:
                storage = SessionStorage.objects.get(session_key=session_id)
                
                
                if timezone.now() - storage.updated_at < self.max_age:
                    request.session = json.loads(storage.session_data)
                else:
                
                    storage.delete()
                    request._session_id = None
                    
            except SessionStorage.DoesNotExist:
                request._session_id = None
            except json.JSONDecodeError:
                request._session_id = None

        response = self.get_response(request)

        if request.session:
        #If the session is new, generate a random ID.   
            if not request._session_id:
                request._session_id = str(uuid.uuid4())

            SessionStorage.objects.update_or_create(
                session_key=request._session_id,
                defaults={'session_data': json.dumps(request.session)}
            )
            # Storing the ID in the user's cookie.
            response.set_cookie(
                self.cookie_name, 
                request._session_id, 
                httponly=True, 
                samesite='Lax'
            )

        return response
