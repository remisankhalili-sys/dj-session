from django.utils.deprecation import MiddlewareMixin
import json

class SimpleCookieSessionMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        self.get_response = get_response
        self.cookie_name = 'my_custom_session'

    def __call__(self, request):
        
        session_data = request.COOKIES.get(self.cookie_name)
        
        if session_data:
            try:
                
                request.session = json.loads(session_data)
            except json.JSONDecodeError:
                request.session = {}
        else:
            
            request.session = {}

       
        response = self.get_response(request)

       
        response.set_cookie(self.cookie_name, json.dumps(request.session), httponly=True)
        
        return response
