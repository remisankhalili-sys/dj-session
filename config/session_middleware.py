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

        # --- 3. Save session back to cookie ---
        # Only save if there is actually something in the session
        if request.session:
            try:
                # Convert dict to JSON string
                json_data = json.dumps(request.session)
                # Sign the JSON string
                signed_data = self.signer.sign(json_data)
                # Set the signed string as the cookie value
                # We add 'httponly=True' for extra security against XSS
                response.set_cookie(
                    self.cookie_name, 
                    signed_data, 
                    httponly=True, 
                    samesite='Lax'
                )
            except Exception as e:
                # In a real production app, you might want to log this error
                print(f"Error signing session: {e}")

        return response

