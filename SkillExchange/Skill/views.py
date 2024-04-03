from django.shortcuts import render, redirect, get_object_or_404
import requests
from django.db import models
from django.http import Http404
from django.views.decorators.http import require_GET
from django.db.models import Q
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import login, authenticate, logout
from .models import CustomUser, UserSkill, UserLocation, Follower, SkillRequest, Notification, SkillSession, SkillPoints, SkillPointsTransactionHistory, SkillPointRequest, CollabRequest, CollabSession, Message, PreferredSkill, Community, Resource, CommunityChatMessage, Event
from django.contrib.auth.decorators import login_required
from .forms import CustomUserChangeForm, UserLocationForm, SkillSessionForm, ReviewForm, SkillPointRequestForm, CollabSessionForm, SkillForm, PreferredSkillsForm, CreateCommunityForm, ResourceUploadForm, EventForm
from django.http import JsonResponse
from django.http import HttpResponse
from django.contrib import messages
from .forms import SkillForm, UserSearchForm
from django.contrib.auth import get_user
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.contrib.auth.decorators import user_passes_test
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from datetime import timedelta
import razorpay
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from django.conf import settings
from django.views.decorators.cache import never_cache
from django.db.models import Max

logger = logging.getLogger(__name__)


# Create your views here.

def index(request):
    return render(request, 'index.html')


@login_required(login_url='login')
@never_cache
def home(request):
    notifications = Notification.objects.filter(
        recipient=request.user, is_read=False)
    return render(request, 'home.html',  {'notifications': notifications})


def mark_as_read(request, notification_id):
    notification = get_object_or_404(
        Notification, id=notification_id, recipient=request.user, is_read=False)
    notification.is_read = True
    notification.save()
    return redirect('home')


def clear_all_notifications(request):
    if request.method == 'POST':
        Notification.objects.filter(recipient=request.user).delete()
    return redirect('home')


def get_notification_status(request):
    notifications = Notification.objects.filter(
        recipient=request.user, is_read=False
    )
    has_new_notifications = notifications.exists()

    return JsonResponse({'hasNewNotifications': has_new_notifications})


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

    # For regular users, attempt to authenticate
        user = authenticate(request, username=username, password=password)
        if user is not None and not user.is_superuser:
            login(request, user)
            request.session['username'] = user.username
            return redirect('home')
        elif user is not None and user.is_superuser:
            login(request, user)
            request.session['username'] = user.username
            return redirect('admin_index')
        else:
            # Set the error message
            messages.error(request, 'Invalid credentials!!')
            return render(request, 'login.html')

    return render(request, 'login.html')


@login_required(login_url='login')
def follow_user(request):
    if 'nf' in request.GET:
        condition = request.GET['nf']
        other_UserID = request.GET['id']
        otherF = CustomUser.objects.get(id=other_UserID)
        foll = Follower(follower=request.user,
                        following=otherF, is_following=True)
        foll.save()

        # Create a notification for the user being followed
        Notification.objects.create(
            recipient=otherF,
            message=f"{request.user.username} has started following you."
        )

    elif 'f' in request.GET:
        condition = request.GET['f']
        other_UserID = request.GET['id']
        otherF = CustomUser.objects.get(id=other_UserID)
        foll, created = Follower.objects.get_or_create(
            follower=request.user,
            following=otherF,
            defaults={'is_following': True}
        )
        if not created:
            foll.is_following = True
            foll.save()

            # Create a notification for the user being followed
            Notification.objects.create(
                recipient=otherF,
                message=f"{request.user.username} has started following you."
            )

    else:
        condition = request.GET['uf']
        other_UserID = request.GET['id']
        otherF = CustomUser.objects.get(id=other_UserID)
        foll = get_object_or_404(
            Follower, follower=request.user, following=otherF, is_following=True)
        foll.is_following = False
        foll.save()

    # Update the 'follow' variable
    data = {
        'user': otherF,
        'user_skills': otherF.skills.all(),
        'follow': Follower.objects.filter(Q(follower=request.user) & Q(following=otherF)).first()
    }

    return render(request, 'profile.html', data)


@login_required
def view_followers(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    followers = Follower.objects.filter(following=user, is_following=True)
    return render(request, 'followers.html', {'user': user, 'followers': followers})


@login_required
def view_following(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    following = Follower.objects.filter(follower=user, is_following=True)
    return render(request, 'following.html', {'user': user, 'following': following})


@login_required(login_url='login')
@never_cache
def edit_profile(request):
    if request.method == 'POST':
        if not UserLocation.objects.filter(user=request.user.id).exists():
            us_loc = CustomUser.objects.get(id=request.user.id)
            city = request.POST['selectedCity']
            state = request.POST['selectedState']
            country = request.POST['selectedCountry']
            location = UserLocation(
                country=country, state=state, city=city, user=us_loc)
            location.save()
        else:
            location = UserLocation.objects.get(user=request.user.id)
            location.country = request.POST['selectedCountry']
            location.state = request.POST['selectedState']
            location.city = request.POST['selectedCity']
            location.save()
        form = CustomUserChangeForm(
            request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
        # user_location = UserLocation.objects.get(id=request.user.id)
        return redirect('profile')
    else:
        form = CustomUserChangeForm(instance=request.user)

    return render(request, 'edit_profile.html', {'form': form,
                                                 'location_form': False,
                                                 'user_location': False,
                                                 })


@login_required(login_url='login')
@never_cache
def view_profile(request):
    user_profile = CustomUser.objects.get(id=request.user.id)
    received_reviews = user_profile.received_reviews.all()

    # Fetch the UserLocation data for the user
    try:
        user_location = UserLocation.objects.get(user=user_profile)
    except UserLocation.DoesNotExist:
        user_location = None

    user_skills = user_profile.skills.all()

    # Check if the logged-in user is following the displayed user
    is_following = False
    if request.user.is_authenticated:
        is_following = Follower.objects.filter(
            follower=request.user, following=user_profile).exists()

    return render(request, 'profile.html', {
        'user_profile': user_profile,
        'user_skills': user_skills,
        'user_location': user_location,
        'is_following': is_following,
        'received_reviews': received_reviews,
        # 'skill_categories': skill_categories,
    })


@login_required(login_url='login')
@never_cache
def view_other_user_profile(request, username):
    user_profile = CustomUser.objects.get(username=username)
    user_skills = user_profile.skills.all()
    try:
        user_location = UserLocation.objects.get(user=user_profile)
    except UserLocation.DoesNotExist:
        user_location = None
    data = {
        'user': user_profile,
        'user_location': user_location,
        'user_skills': user_skills,
        'follow': False
    }
    if Follower.objects.filter(follower=request.user.id).exists():
        if Follower.objects.filter(Q(follower=request.user.id) & Q(following=user_profile.id)).exists():
            follow = Follower.objects.get(
                Q(follower=request.user.id) & Q(following=user_profile.id))
            data['follow'] = follow
    return render(request, 'profile.html', data)


def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('login')


@login_required(login_url='login')
@never_cache
def admin_index(request):
    all_users = CustomUser.objects.exclude(
        is_superuser='1')  # Exclude superusers
    user_count = all_users.count()
    context = {
        "all_users": all_users,
        "user_count": user_count
    }
    return render(request, 'admin_index.html', context)


@login_required(login_url='login')
def add_skill(request):
    if request.method == 'POST':
        skill_form = SkillForm(request.POST)
        if skill_form.is_valid():
            skill = skill_form.save(commit=False)
            skill.user = request.user
            skill.save()
            return redirect('profile')
    else:
        skill_form = SkillForm()

    context = {'skill_form': skill_form}
    return render(request, 'add_skill.html', context)


def select_preferred_skills(request):
    if request.method == 'POST':
        form = PreferredSkillsForm(request.POST)

        if form.is_valid():
            # Clear existing preferred skills for the user
            request.user.preferred_skills.all().delete()

            # Save the selected skills
            for skill in form.cleaned_data['skill_categories']:
                PreferredSkill.objects.create(user=request.user, skill=skill)

            return redirect('profile')
    else:
        form = PreferredSkillsForm()

    return render(request, 'preferred_skills.html', {'form': form})


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
        # subject = 'Account Deactivation'
        # message = 'Your account has been deactivated by the admin.'
        # from_email = 'jeevaragnp2024b@mca.ajce.in'  # Replace with your email
        # recipient_list = [user.email]
        # html_message = render_to_string(
        #     'deactivation_mail.html', {'user': user})

        # send_mail(subject, message, from_email,
        #           recipient_list, html_message=html_message)

    else:
        messages.warning(
            request, f"User '{user.username}' is already deactivated.")
    return redirect('admin_index')


def activate_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if not user.is_active:
        user.is_active = True
        user.save()
        # subject = 'Account activated'
        # message = 'Your account has been activated.'
        # from_email = 'jeevaragnp2024b@mca.ajce.in'  # Replace with your email
        # recipient_list = [user.email]
        # html_message = render_to_string('activation_mail.html', {'user': user})

        # send_mail(subject, message, from_email,
        #           recipient_list, html_message=html_message)
    else:
        messages.warning(request, f"User '{user.username}' is already active.")
    return redirect('admin_index')


def contact(request):
    return render(request, 'contact.html')


def about_us(request):
    return render(request, 'about_us.html')


def learn(request):
    users = CustomUser.objects.exclude(Q(is_superuser='1') | Q(
        id=request.user.id))  # Exclude superusers
    user_count = users.count()
    context = {
        "users": users,
        "user_count": user_count
    }
    return render(request, 'learn.html', context)


def teach(request):
    users = CustomUser.objects.exclude(Q(is_superuser='1') | Q(
        id=request.user.id))  # Exclude superusers
    user_count = users.count()
    context = {
        "users": users,
        "user_count": user_count
    }
    return render(request, 'teach.html', context)


def send_skill_request(request, receiver_id):
    if request.method == 'POST':
        receiver = get_object_or_404(CustomUser, id=receiver_id)
        message = request.POST.get('message')
        SkillRequest.objects.create(
            sender=request.user, receiver=receiver, message=message, status='pending')
        # Redirect to a success page or user profile
        Notification.objects.create(
            recipient=receiver,
            message=f"New Skill request from {request.user.username}."
        )

        return redirect('profile', username=receiver.username)


def accept_skill_request(request, request_id):
    if request.method == 'POST':
        skill_request = get_object_or_404(
            SkillRequest, id=request_id, receiver=request.user, status='pending')
        skill_request.status = 'accepted'
        skill_request.save()

        Notification.objects.create(
            recipient=skill_request.sender,
            message=f"Your skill request has been accepted by {
                request.user.username}."
        )

        # Redirect to a form for scheduling the session
        return redirect('schedule_session', request_id=skill_request.id)


def reject_skill_request(request, request_id):
    if request.method == 'POST':
        skill_request = get_object_or_404(
            SkillRequest, id=request_id, receiver=request.user, status='pending')
        skill_request.status = 'rejected'
        skill_request.save()

        Notification.objects.create(
            recipient=skill_request.sender,
            message=f"Your skill request has been rejected by {
                request.user.username}."
        )
        # Redirect to a success page or user profile
        return redirect('profile', username=request.user.username)


def send_collab_request(request, receiver_id):
    if request.method == 'POST':
        receiver = get_object_or_404(CustomUser, id=receiver_id)
        message = request.POST.get('message')
        CollabRequest.objects.create(
            sender=request.user, receiver=receiver, status='pending')

        Notification.objects.create(
            recipient=receiver,
            message=f"New Collaboration request from {request.user.username}."
        )

        # Redirect to a success page or user profile
        return redirect('profile', username=receiver.username)


def accept_collab_request(request, request_id):
    if request.method == 'POST':
        collab_request = get_object_or_404(
            CollabRequest, id=request_id, receiver=request.user, status='pending')
        collab_request.status = 'accepted'
        collab_request.save()

        Notification.objects.create(
            recipient=collab_request.sender,
            message=f"Your Collab request has been rejected by {
                request.user.username}."
        )
        # Redirect to a form for scheduling the session
        return redirect('schedule_collab', request_id=collab_request.id)


def reject_collab_request(request, request_id):
    if request.method == 'POST':
        collab_request = get_object_or_404(
            CollabRequest, id=request_id, receiver=request.user, status='pending')
        collab_request.status = 'rejected'
        collab_request.save()

        Notification.objects.create(
            recipient=collab_request.sender,
            message=f"Your Collab request has been rejected by {
                request.user.username}."
        )
        # Redirect to a success page or user profile
        return redirect('profile', username=request.user.username)


def collab_requests(request):
    pending_requests = CollabRequest.objects.filter(
        receiver=request.user, status='pending')
    return render(request, 'collab_request.html', {'pending_requests': pending_requests})


def sent_collab_requests(request):
    # Fetch the skill requests sent by the current user
    sent_requests = CollabRequest.objects.filter(sender=request.user)
    return render(request, 'sent_collab_requests.html', {'sent_requests': sent_requests})


def schedule_collab(request, request_id):
    collab_request = get_object_or_404(
        CollabRequest, id=request_id, receiver=request.user, status='accepted')

    if request.method == 'POST':
        form = CollabSessionForm(request.POST)
        if form.is_valid():
            date_and_time = form.cleaned_data['date_and_time']

            # Create a session for the accepted skill request
            CollabSession.objects.create(
                collab_request=collab_request,
                date_and_time=date_and_time,
                status='scheduled'
            )

            Notification.objects.create(
                recipient=collab_request.sender,
                message=f"Collab scheduled with {
                    request.user.username} on {date_and_time}."
            )

            messages.success(request, 'Collab session scheduled successfully!')
            return redirect('profile', username=request.user.username)
    else:
        form = CollabSessionForm()

    return render(request, 'schedule_collab.html', {'form': form, 'collab_request': collab_request})


def collab_schedule(request):
    # Fetch all skill sessions for the current user, regardless of status, and order by status
    collab_sessions = CollabSession.objects.filter(
        Q(collab_request__receiver=request.user) | Q(
            collab_request__sender=request.user)
    ).order_by('-status')

    return render(request, 'collab_schedule.html', {'collab_sessions': collab_sessions})


def request_skill_points(request, receiver_id):
    receiver = get_object_or_404(CustomUser, id=receiver_id)

    # Filter SkillRequest objects where the current user is the sender and status is 'pending'
    skill_request = SkillRequest.objects.filter(
        receiver=request.user, status='pending').first()

    if not skill_request:
        # Raise an Http404 error or redirect to an appropriate page
        HttpResponse("No pending SkillRequest found for the current user.")

    if request.method == 'POST':
        form = SkillPointRequestForm(request.POST)
        if form.is_valid():
            points_requested = form.cleaned_data['points_requested']

            # Create a skill point request
            SkillPointRequest.objects.create(
                sender=request.user,
                receiver=receiver,
                skill_request=skill_request,
                points_requested=points_requested
            )

            return redirect('profile')

    else:
        form = SkillPointRequestForm()

    return render(request, 'request_skill_points.html', {'form': form, 'receiver': receiver})


@never_cache
def skillpoint_request(request):
    received_requests = SkillPointRequest.objects.filter(
        receiver=request.user, status='pending')
    print("Received Requests:", received_requests)
    return render(request, 'skillpoint_request.html', {'received_requests': received_requests})


def accept_skillpoint_request(request, request_id):
    skill_point_request = get_object_or_404(
        SkillPointRequest, id=request_id, receiver=request.user)

    if request.method == 'POST':
        if skill_point_request.status == 'pending':
            # Deduct points from sender and add points to the receiver
            sender_skill_points = SkillPoints.objects.get(
                user=skill_point_request.sender)
            receiver_skill_points = SkillPoints.objects.get(user=request.user)

            if sender_skill_points.available_points >= skill_point_request.points_requested:
                sender_skill_points.available_points -= skill_point_request.points_requested
                sender_skill_points.spent_points += skill_point_request.points_requested
                sender_skill_points.save()

                receiver_skill_points.available_points += skill_point_request.points_requested
                receiver_skill_points.received_points += skill_point_request.points_requested
                receiver_skill_points.save()

                skill_point_request.status = 'accepted'
                skill_point_request.save()

                # Update the corresponding skill request status
                skill_request = skill_point_request.skill_request
                if skill_request and skill_request.status == 'pending':
                    skill_request.status = 'accepted'
                    skill_request.save()

    return redirect('skillpoint_request_status')


def reject_skillpoint_request(request, request_id):
    skill_point_request = get_object_or_404(
        SkillPointRequest, id=request_id, receiver=request.user)

    if request.method == 'POST':
        if skill_point_request.status == 'pending':
            skill_point_request.status = 'rejected'
            skill_point_request.save()

    return redirect('profile')


@never_cache
def skillpoint_request_status(request):
    sent_requests = SkillPointRequest.objects.filter(sender=request.user)
    return render(request, 'skillpoint_request_status.html', {'sent_requests': sent_requests})


def skill_requests(request):
    pending_requests = SkillRequest.objects.filter(
        receiver=request.user, status='pending')
    return render(request, 'skill_requests.html', {'pending_requests': pending_requests})


@never_cache
def sent_skill_requests(request):
    # Fetch the skill requests sent by the current user
    sent_requests = SkillRequest.objects.filter(sender=request.user)
    return render(request, 'sent_skill_requests.html', {'sent_requests': sent_requests})


def schedule_session(request, request_id):
    skill_request = get_object_or_404(
        SkillRequest, id=request_id, receiver=request.user, status='accepted')

    if request.method == 'POST':
        form = SkillSessionForm(request.POST)
        if form.is_valid():
            date_and_time = form.cleaned_data['date_and_time']
            duration_minutes = form.cleaned_data['duration_minutes']

            # Create a session for the accepted skill request
            SkillSession.objects.create(
                skill_request=skill_request,
                date_and_time=date_and_time,
                duration_minutes=duration_minutes,
                status='scheduled'
            )

            messages.success(request, 'Skill session scheduled successfully!')
            return redirect('profile', username=request.user.username)
    else:
        form = SkillSessionForm()

    return render(request, 'schedule_session.html', {'form': form, 'skill_request': skill_request})


def schedule_session_skillpoint(request, request_id):
    skill_point_request = get_object_or_404(
        SkillPointRequest, id=request_id, sender=request.user, status='accepted')

    if request.method == 'POST':
        form = SkillSessionForm(request.POST)
        if form.is_valid():
            date_and_time = form.cleaned_data['date_and_time']
            duration_minutes = form.cleaned_data['duration_minutes']

            # Create a session for the accepted skill point request
            SkillSession.objects.create(
                skill_request=skill_point_request.skill_request,
                date_and_time=date_and_time,
                duration_minutes=duration_minutes,
                status='scheduled'
            )

            messages.success(request, 'Skill session scheduled successfully!')
            return redirect('profile', username=request.user.username)
    else:
        form = SkillSessionForm()

    # Check if the status is not "accepted"
    if skill_point_request.status != 'accepted':
        messages.error(request, 'Skill point request is not accepted.')
        return redirect('profile')  # Redirect to the profile page

    return render(request, 'schedule_session.html', {'form': form, 'skill_request': skill_point_request.skill_request})


def manage_session(request, session_id):
    skill_session = get_object_or_404(SkillSession, id=session_id)

    # Check if the current user is either the sender or the receiver
    is_sender = skill_session.skill_request.sender == request.user
    is_receiver = skill_session.skill_request.receiver == request.user

    if not is_sender and not is_receiver:
        messages.error(
            request, 'You do not have permission to manage this session.')
        return redirect('profile')  # Redirect to an appropriate page

    # Check if the current time is within the scheduled time window
    current_time = timezone.now()
    scheduled_start_time = skill_session.date_and_time
    scheduled_end_time = scheduled_start_time + \
        timedelta(minutes=skill_session.duration_minutes)

    if current_time > scheduled_end_time and skill_session.status == 'scheduled':
        if is_receiver:
            skill_session.receiver_status = 'absent'
        elif is_sender:
            skill_session.sender_status = 'absent'
        skill_session.status = 'expired'
        skill_session.save()
        messages.success(request, 'Session status updated to "absent".')

        return redirect('profile')

    if current_time < scheduled_start_time or current_time > scheduled_end_time:
        messages.error(
            request, 'Session has not started or has already ended.')
        return redirect('profile')  # Redirect to an appropriate page

    if request.method == 'POST':
        if skill_session.status == 'scheduled':  # Only allow updates if the session is still scheduled
            if 'mark_attended' in request.POST:
                if is_receiver:
                    skill_session.receiver_status = 'attended'
                elif is_sender:
                    skill_session.sender_status = 'attended'

                # Check if both sender and receiver have attended
                if skill_session.sender_status == 'attended' and skill_session.receiver_status == 'attended':
                    skill_session.status = 'completed'
            else:
                if is_receiver:
                    skill_session.receiver_status = 'absent'
                elif is_sender:
                    skill_session.sender_status = 'absent'

                # Check if both sender and receiver are absent
                if skill_session.sender_status == 'absent' and skill_session.receiver_status == 'absent':
                    skill_session.status = 'abandoned'
                else:
                    skill_session.status = 'expired'

            skill_session.save()
            messages.success(request, 'Session status updated successfully.')
            return redirect('profile')

    return render(request, 'manage_sessions.html', {'skill_session': skill_session})


def video_call(request):
    return render(request, 'videocall.html')


def join_video(request):
    if request.method == 'POST':
        roomID = request.POST['roomID']
        return redirect("/video_chat_room?roomID=" + roomID)
    return render(request, 'join_call.html')


def session_schedule(request):
    # Fetch all skill sessions for the current user, regardless of status, and order by status
    skill_sessions = SkillSession.objects.filter(
        Q(skill_request__receiver=request.user) | Q(
            skill_request__sender=request.user)
    ).order_by('-status')

    return render(request, 'session_schedule.html', {'skill_sessions': skill_sessions})


def create_review(request, session_id):
    skill_session = get_object_or_404(SkillSession, id=session_id)

    if skill_session.status != 'completed':
        messages.error(request, 'You can only review completed sessions.')
        return redirect('profile')  # Adjust the redirect as needed

    # Check if the current user is allowed to review
    if request.user != skill_session.skill_request.sender:
        messages.error(request, 'You are not allowed to review this session.')
        return redirect('profile')  # Adjust the redirect as needed

    if request.method == 'POST':
        # Assuming you have a ReviewForm to handle the creation
        form = ReviewForm(request.POST)

        if form.is_valid():
            # Create a new review instance and link it to the skill session
            review = form.save(commit=False)
            review.sender = request.user
            review.receiver = skill_session.skill_request.receiver
            review.skill_session = skill_session
            review.save()
            messages.success(request, 'Review posted successfully.')
            return redirect('profile')  # Adjust the redirect as needed

            # Other logic, redirect, or render as needed
    else:
        form = ReviewForm()  # Assuming you have a ReviewForm

    return render(request, 'create_review.html', {'form': form, 'skill_session': skill_session})


def buy_skillpoints(request):
    return render(request, 'buy_points.html')


def pay_razor(request):
    if request.method == "POST":
        name = request.POST.get('name')

        client = razorpay.Client(
            auth=("rzp_test_4xk0xz87l8Atss", "7zBFnTLQvHPXVUseIuZbB1lq"))

        payment = client.order.create({
            'amount': 30000,
            'currency': 'INR',
            "receipt": "receipt#1",
            'payment_capture': '1'})

        # Update SkillPointsTransactionHistory model
        transaction = SkillPointsTransactionHistory.objects.create(
            user=request.user,
            skill_points=300,  # Update based on your logic
            amount_paid=amount / 100.0,  # Convert amount to rupees
            purchase_time=timezone.now()
        )

        # Update SkillPoints model
        skill_points, created = SkillPoints.objects.get_or_create(
            user=request.user)
        skill_points.available_points += 300  # Update based on your logic
        skill_points.save()

    return render(request, 'pay_razor.html')


@csrf_exempt
def success(request):
    return render(request, "success.html")

# @login_required
# def chat(request):
#     return render(request, 'chat.html')


@login_required
def display_users(request):
    # Get a list of unique users with whom the current user has chatted
    users = CustomUser.objects.filter(
        Q(sent_messages__receiver=request.user) | Q(
            received_messages__sender=request.user)
    ).distinct()

    return render(request, 'display_users.html', {'users': users})


@login_required
def chat(request, receiver_id=None):
    # Get a list of unique users with whom the current user has chatted
    users = CustomUser.objects.filter(
        Q(sent_messages__receiver=request.user) | Q(
            received_messages__sender=request.user)
    ).distinct()

    if receiver_id:
        # If a specific receiver_id is provided, retrieve the corresponding user
        receiver = get_object_or_404(CustomUser, id=receiver_id)
        # Get the messages between the current user and the selected receiver
        messages = Message.objects.filter(
            Q(sender=request.user, receiver=receiver) | Q(
                sender=receiver, receiver=request.user)
        ).order_by('timestamp')
    else:
        # If no receiver_id is provided, set the receiver to the first user in the list (if available)
        receiver = users.first()
        if receiver:
            # Get the messages between the current user and the default receiver
            messages = Message.objects.filter(
                Q(sender=request.user, receiver=receiver) | Q(sender=receiver, receiver=request.user)).order_by('timestamp')
        else:
            messages = []

    return render(request, 'chat.html', {'receiver': receiver, 'messages': messages, 'users': users, 'selected_receiver_id': int(receiver_id) if receiver_id else None})


@login_required
def send_message(request):
    if request.method == 'POST':
        receiver_id = request.POST.get('receiver_id')
        content = request.POST.get('content')

        try:
            receiver = CustomUser.objects.get(id=receiver_id)
            message = Message.objects.create(
                sender=request.user, receiver=receiver, content=content)
            messages.success(request, 'Message sent successfully!')
        except CustomUser.DoesNotExist:
            messages.error(request, 'Receiver not found.')

    return redirect('chat', receiver_id=receiver_id)


def community_home(request):
    if request.method == 'POST' and 'join_community' in request.POST:
        # Handle joining community logic here
        community_id = request.POST.get('community_id')
        community_to_join = Community.objects.get(id=community_id)
        community_to_join.members.add(request.user)
        community_to_join.save()
        # Add the leader as a member if not already a member
        if request.user != community_to_join.leader:
            community_to_join.members.add(community_to_join.leader)
        # Add an alert message to inform the user
        messages.success(request, 'Joined community successfully!')

    create_community_form = CreateCommunityForm()
    communities_created = Community.objects.filter(leader=request.user)
    communities_joined = request.user.joined_communities.all()
    communities_available = Community.objects.exclude(
        leader=request.user).exclude(members=request.user)

    # Fetch upcoming events for all communities
    for community in communities_joined:
        community.upcoming_events = Event.objects.filter(community=community, timestamp__gte=timezone.now()).order_by('timestamp')[:5]
    for community in communities_available:
        community.upcoming_events = Event.objects.filter(community=community, timestamp__gte=timezone.now()).order_by('timestamp')[:5]

    return render(request, 'community_home.html', {
        'create_community_form': create_community_form,
        'communities_created': communities_created,
        'communities_joined': communities_joined,
        'communities_available': communities_available,
    })


def create_community(request):
    if request.method == 'POST':
        form = CreateCommunityForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the form data to create a new community
            community = form.save(commit=False)
            # Assuming you have a 'leader' field in your Community model
            community.leader = request.user
            community.save()
            # Add the leader as a member of the community
            community.members.add(request.user)
            # Optionally, you can redirect to a different page after successful creation
            # Redirect to the home page or any other page
            return redirect('community_home')
    else:
        form = CreateCommunityForm()  # Create a new form instance if it's a GET request

    return render(request, 'create_community.html', {'form': form})


def community_page(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    members = community.members.all()
    resources = Resource.objects.filter(community=community)
    user = request.user
    # Add any additional context data you want to pass to the template
    return render(request, 'community_page.html', {'community': community, 'members': members, 'resources': resources})


def leave_community(request, community_id):
    try:
        community = Community.objects.get(id=community_id)
        # Check if the user is a member of the community
        if request.user in community.members.all():
            # Remove the user from the community
            community.members.remove(request.user)
            messages.success(
                request, 'You have successfully left the community.')

            # Check if the user leaving is the leader
            if request.user == community.leader:
                # Delete the community if the leaving member is the leader
                community.delete()
                messages.success(
                    request, 'The community has been deleted since the leader left.')
        else:
            messages.warning(request, f'You are not a member of the {
                             community.name} community.')
    except Community.DoesNotExist:
        messages.error(request, 'Community not found.')

    return redirect('community_home')


def resource_upload(request, community_id):
    community = get_object_or_404(Community, id=community_id)

    if request.method == 'POST':
        form = ResourceUploadForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.user = request.user
            resource.community = community
            resource.save()
            return redirect('resource_upload', community_id=community_id)
    else:
        form = ResourceUploadForm()

    return render(request, 'resource_upload.html', {'form': form, 'community': community, 'MEDIA_URL': settings.MEDIA_URL})


from django.contrib import messages

@login_required
def community_chat(request, community_id):
    community = get_object_or_404(Community, id=community_id)
    messages_qs = CommunityChatMessage.objects.filter(community=community).order_by('timestamp')

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            message = CommunityChatMessage.objects.create(sender=request.user, community=community, content=content)
            messages.success(request, 'Message sent successfully!')
            return redirect('community_chat', community_id=community.id)
        else:
            messages.error(request, 'Failed to send message. Please try again.')

    return render(request, 'forum_chat.html', {'community': community, 'messages': messages_qs})


def community_events(request, community_id):
    community = Community.objects.get(id=community_id)
    events = Event.objects.filter(community=community)
    is_leader = community.leader == request.user  # Check if current user is leader

    form = EventForm(request.POST or None)
    if request.method == 'POST' and is_leader:
        if form.is_valid():
            event = form.save(commit=False)
            event.community = community
            event.save()
            return redirect('community_events', community_id=community.id)

    context = {
        'community': community,
        'events': events,
        'form': form,
        'is_leader': is_leader,
    }
    return render(request, 'community_event.html', context)


def create_event(request, community_id):
    community = Community.objects.get(id=community_id)
    form = EventForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            event = form.save(commit=False)
            event.community = community
            event.save()
            return redirect('community_events', community_id=community.id)
    context = {
        'community': community,
        'form': form,
    }
    return render(request, 'create_event.html', context)