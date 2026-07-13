from django.shortcuts import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model

User = get_user_model()


def register(request):
    if User.objects.filter(username='sepehr').exists():
        return HttpResponse("User already exists")

    user = User(
        username='user',
        email='user@gmail.com'
    )
    user.set_password("1234")
    user.save()

    return HttpResponse("User created")


def login_view(request):
    if request.method == "GET":
        username = request.GET.get("username")
        password = request.GET.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return HttpResponse("Logged in successfully")

        return HttpResponse("Invalid username or password")

    return HttpResponse("Send a POST request with username and password.")



def show_session(request):
    return HttpResponse(f'username: {request.user}')

# --- Test View for Custom Session ---
def session_test_view(request):
    # 1. Try to get a value from the custom session
    # If it's the first time, it will return 0
    counter = request.session.get('counter', 0)
    
    # 2. Increment the counter
    counter += 1
    
    # 3. Save the new value back to the session
    request.session['counter'] = counter
    
    # 4. Return a response showing the current counter value
    return HttpResponse(f"Current session counter: {counter}")
