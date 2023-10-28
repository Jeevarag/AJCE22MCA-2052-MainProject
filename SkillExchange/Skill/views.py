from django.shortcuts import render, redirect, get_object_or_404
import requests
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import login, authenticate, logout
from .models import CustomUser, UserSkill
from django.contrib.auth.decorators import login_required
from .forms import CustomUserChangeForm
from django.http import JsonResponse
from django.contrib import messages
from .forms import SkillForm, UserSearchForm 
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.contrib.auth.decorators import user_passes_test
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.contrib.auth import get_user_model


# Create your views here.

def index(request):
    return render(request, 'index.html')

@login_required(login_url='login')
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

        if username == "jeejay" and password == "jee123":
            # For the superuser, redirect to admin_index.html with user list and count
            users = CustomUser.objects.exclude(is_superuser='1')  # Exclude superusers
            user_count = users.count()
            context = {
                "users": users,
                "user_count": user_count
            }
            return render(request, 'admin_index.html', context)
        else:
    # For regular users, attempt to authenticate
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                request.session['username'] = user.username
                return redirect('home')
            else:
                messages.error(request, 'Invalid credentials!!')  # Set the error message
                return render(request, 'login.html')

    return render(request, 'login.html')


@login_required(login_url='login')
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = CustomUserChangeForm(instance=request.user)

    return render(request, 'edit_profile.html', {'form': form})

@login_required(login_url='login')
def view_profile(request):
    user_profile = CustomUser.objects.get(id=request.user.id)
    user_skills = user_profile.skills.all() 
    return render(request, 'profile.html', {'user_profile': user_profile, 'user_skills': user_skills})


@login_required(login_url='login')
def view_other_user_profile(request, username):
    user_profile = CustomUser.objects.get(username=username)
    user_skills = user_profile.skills.all()

    return render(request, 'profile.html', {'user': user_profile, 'user_skills': user_skills})


def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('login')

@login_required(login_url='login')
def admin_index(request):
    return render(request, 'admin_index.html')


@login_required(login_url='login')
def add_skill(request):
    if request.method == 'POST':
        skill_form = SkillForm(request.POST)
        if skill_form.is_valid():
            skill = skill_form.save(commit=False)
            skill.user = request.user  # Link the skill to the authenticated user
            skill.save()
            return redirect('profile')  # Redirect to the profile page after adding the skill
    else:
        skill_form = SkillForm()

    context = {
        'skill_form': skill_form 
    }

    return render(request, 'add_skill.html', context)


def search_users(request):
    if request.method == 'GET':
        form = UserSearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            users_with_skill = UserSkill.objects.filter(name__icontains=query)
            return render(request, 'search_results.html', {'users_with_skill': users_with_skill})
        else:
            form = UserSearchForm()
        return render(request, 'home.html', {'form': form})


def deactivate_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if user.is_active:
        user.is_active = False
        user.save()
         # Send deactivation email
        subject = 'Account Deactivation'
        message = 'Your account has been deactivated by the admin.'
        from_email = 'jeevaragnp2024b@mca.ajce.in'  # Replace with your email
        recipient_list = [user.email]
        html_message = render_to_string('deactivation_mail.html', {'user': user})

        send_mail(subject, message, from_email, recipient_list, html_message=html_message)

        messages.success(request, f"User '{user.username}' has been deactivated, and an email has been sent.")
    else:
        messages.warning(request, f"User '{user.username}' is already deactivated.")
    return redirect('admin_index')

def activate_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if not user.is_active:
        user.is_active = True
        user.save()
        subject = 'Account activated'
        message = 'Your account has been activated.'
        from_email = 'jeevaragnp2024b@mca.ajce.in'  # Replace with your email
        recipient_list = [user.email]
        html_message = render_to_string('activation_mail.html', {'user': user})

        send_mail(subject, message, from_email, recipient_list, html_message=html_message)
    else:
        messages.warning(request, f"User '{user.username}' is already active.")
    return redirect('admin_index')







