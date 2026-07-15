from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views import View
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterView(View):
    """
    Handles user registration.
    """
    def get(self, request):
        # For simplicity, using a hardcoded user as in your original code
        if User.objects.filter(username='sepehr').exists():
            return HttpResponse("User already exists")

        user = User(
            username='sepehr',
            email='user@gmail.com'
        )
        user.set_password("1234")
        user.save()
        return HttpResponse("User created successfully!")


class LoginView(View):
    """
    Handles user authentication and custom session assignment.
    """
    def get(self, request):
        username = request.GET.get("username")
        password = request.GET.get("password")

        if not username or not password:
            return HttpResponse("Please provide both username and password.")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Custom Session Implementation
            # We are manually injecting data into the session object
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            request.session['is_authenticated'] = True
            
            return redirect('profile') 

        return HttpResponse("Invalid username or password", status=401)


class ProfileView(View):
    """
    Displays user profile if authenticated via custom session.
    """
    def get(self, request):
        # Check authentication via our custom session logic
        is_authenticated = request.session.get('is_authenticated', False)
        
        if is_authenticated:
            username = request.session.get('username')
            user_id = request.session.get('user_id')
            return HttpResponse(f"<h1>Profile Page</h1><p>Welcome, {username}!<br>Your User ID is: {user_id}</p>")
        
        # Redirect to login if not authenticated
        return redirect('login')
    
class SessionStatusView(View):
    """
    Helper view to check the current session status.
    """
    def get(self, request):
        username = request.session.get('username', 'Guest')
        return HttpResponse(f'Current Session Username: {username}')


