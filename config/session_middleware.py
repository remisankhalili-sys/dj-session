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

        if cookie_value:
            try:
                # Attempt to unsign and verify the data
                # If someone tampered with the cookie, this raises BadSignature
                decoded_data = self.signer.unsign(cookie_value)
                session_data = json.loads(decoded_data)
            except (BadSignature, json.JSONDecodeError, Exception):
                # If signature is invalid or data is corrupted, 
                # we treat it as an empty session (security first!)
                session_data = {}

        # Attach the session dictionary to the request object
        request.session = session_data

        # --- 2. Process the request ---
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

