from django.shortcuts import render, redirect
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import login, authenticate, logout
from .models import CustomUser, UserSkill
from django.contrib.auth.decorators import login_required
from .forms import CustomUserChangeForm
from django.http import JsonResponse
from .forms import SkillForm 
from django.contrib import messages


# Create your views here.

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


from django.contrib import messages

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
                # Add an error message
                messages.error(request, 'Invalid credentials!!')

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

