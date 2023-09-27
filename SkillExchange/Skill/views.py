from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .models import CustomUser
from django.contrib.auth.decorators import login_required

# Create your views here.


def home(request):
    return render(request, 'home.html')


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            return render(request, 'registration.html', {'error_message': 'Passwords do not match'})

        # Create a user instance but do not save it yet
        user = CustomUser(username=username, email=email)

        # Set the password for the user
        user.set_password(password)

        # Save the user to the database
        user.save()

        # Redirect to the home page or any desired page
        return redirect('login')

    return render(request, 'registration.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            request.session['username'] = user.username
            return redirect('home')
        else:
            return render(request, 'login.html', {'error_message': 'Invalid credentials!!'})

    return render(request, 'login.html')


def user_logout(request):
    logout(request)
    return redirect('login')


#comment