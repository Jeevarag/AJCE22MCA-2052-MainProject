from django.shortcuts import render, redirect, get_object_or_404
import requests
from django.http import Http404
from django.db.models import Q
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import login, authenticate, logout
from .models import CustomUser, UserSkill, UserLocation, Follower, SkillRequest, Notification, SkillSession, SkillPoints, SkillPointsTransactionHistory, SkillPointRequest
from django.contrib.auth.decorators import login_required
from .forms import CustomUserChangeForm, UserLocationForm, SkillSessionForm, ReviewForm,SkillPointRequestForm
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
from .skills import SKILLS
from django.utils import timezone
from datetime import timedelta
import razorpay
from django.views.decorators.csrf import csrf_exempt
import json
import logging

logger = logging.getLogger(__name__)


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
        return redirect('profile')
    elif 'f' in request.GET:
        condition = request.GET['f']
        other_UserID = request.GET['id']
        otherF = CustomUser.objects.get(id=other_UserID)
        foll = Follower.objects.get(
            Q(follower=request.user) & Q(following=other_UserID))
        foll.is_following = True
        foll.save()
        return redirect('profile')
    else:
        condition = request.GET['uf']
        other_UserID = request.GET['id']
        otherF = CustomUser.objects.get(id=other_UserID)
        try:
            foll = Follower.objects.get(
                follower=request.user, following=otherF, is_following=False)
            foll.delete()
        except Follower.DoesNotExist:
            pass
        return redirect('profile')


@login_required(login_url='login')
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
        'user_skills': user_profile.skills.all(),
        'user_location': user_location,
        'is_following': is_following,
        'received_reviews': received_reviews,
    })


@login_required(login_url='login')
def view_other_user_profile(request, username):
    user_profile = CustomUser.objects.get(username=username)
    user_skills = user_profile.skills.all()
    data = {
        'user': user_profile,
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
            skill.user = request.user  # Link the skill to the authenticated user
            skill.save()
            # Redirect to the profile page after adding the skill
            return redirect('profile')
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
        html_message = render_to_string(
            'deactivation_mail.html', {'user': user})

        send_mail(subject, message, from_email,
                  recipient_list, html_message=html_message)

    else:
        messages.warning(
            request, f"User '{user.username}' is already deactivated.")
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

        send_mail(subject, message, from_email,
                  recipient_list, html_message=html_message)
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
        return redirect('profile', username=receiver.username)


def accept_skill_request(request, request_id):
    if request.method == 'POST':
        skill_request = get_object_or_404(
            SkillRequest, id=request_id, receiver=request.user, status='pending')
        skill_request.status = 'accepted'
        skill_request.save()

        # Redirect to a form for scheduling the session
        return redirect('schedule_session', request_id=skill_request.id)


def reject_skill_request(request, request_id):
    if request.method == 'POST':
        skill_request = get_object_or_404(
            SkillRequest, id=request_id, receiver=request.user, status='pending')
        skill_request.status = 'rejected'
        skill_request.save()
        # Redirect to a success page or user profile
        return redirect('profile', username=request.user.username)


def request_skill_points(request, receiver_id):
    receiver = get_object_or_404(CustomUser, id=receiver_id)
    skill_request = SkillRequest.objects.filter(
        sender=request.user, status='pending').first()
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

def skillpoint_request(request):
    received_requests = SkillPointRequest.objects.filter(receiver=request.user, status='pending')
    print("Received Requests:", received_requests)
    return render(request, 'skillpoint_request.html', {'received_requests': received_requests})

def accept_skillpoint_request(request, request_id):
    skill_point_request = get_object_or_404(SkillPointRequest, id=request_id, receiver=request.user)
    
    if request.method == 'POST':
        if skill_point_request.status == 'pending':
            # Deduct points from sender and add points to the receiver
            sender_skill_points = SkillPoints.objects.get(user=skill_point_request.sender)
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
    skill_point_request = get_object_or_404(SkillPointRequest, id=request_id, receiver=request.user)

    if request.method == 'POST':
        if skill_point_request.status == 'pending':
            skill_point_request.status = 'rejected'
            skill_point_request.save()

    return redirect('profile')

def skillpoint_request_status(request):
    sent_requests = SkillPointRequest.objects.filter(sender=request.user)
    return render(request, 'skillpoint_request_status.html', {'sent_requests': sent_requests})


def skill_requests(request):
    pending_requests = SkillRequest.objects.filter(
        receiver=request.user, status='pending')
    return render(request, 'skill_requests.html', {'pending_requests': pending_requests})


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
    print(f"DEBUG: Received request_id: {request_id}")
    skill_point_request = get_object_or_404(SkillPointRequest, id=request_id, receiver=request.user, status='accepted')
    print(f"DEBUG: SkillPointRequest Status: {skill_point_request.status}")

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


def buy_skill_points(request):

    return render(request, "buy_points.html",)

@csrf_exempt
def purchase_skillpoints(request):
    logger.info("Purchase Skill Points view called")
    if request.method == 'POST':
        # Get the selected plan value from the form
        selected_plan = request.POST.get('selected_plan', '')

        # Check if the value is non-empty and numeric
        if selected_plan.isdigit() and int(selected_plan) > 0:
            points_plan = int(selected_plan)

            # Replace with your actual Razorpay API key and secret
            razorpay_key_id = "rzp_test_4xk0xz87l8Atss"
            razorpay_key_secret = "7zBFnTLQvHPXVUseIuZbB1lq"

            client = razorpay.Client(auth=(razorpay_key_id, razorpay_key_secret))

            # Create an order on Razorpay
            order_data = {
                "amount": points_plan * 100,  # Convert to paise
                "currency": "INR",
                "receipt": f"skill_points_receipt_{request.user.id}",
                "notes": {
                    "user_id": request.user.id,
                    "plan": f"{points_plan} Skill Points",
                }
            }

            order = client.order.create(data=order_data)

            # Pass order ID and other details to the client-side
            context = {
                "razorpay_key_id": razorpay_key_id,
                "order_id": order['id'],
                "order_amount": order['amount'],
            }
            print("Redirecting to payment view")
            return redirect('payment_view', order_id=order['id'])

    return render(request, 'buy_points.html')


def payment_view(request):
    # Replace with your actual Razorpay API key and secret
    razorpay_key_id = "rzp_test_4xk0xz87l8Atss"
    razorpay_key_secret = "7zBFnTLQvHPXVUseIuZbB1lq"

    client = razorpay.Client(auth=(razorpay_key_id, razorpay_key_secret))

    # Handle the Razorpay response and update the necessary data
    if request.method == 'POST':
        data = json.loads(request.body)

        # Extract relevant information from the response
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')

        # Verify the payment signature using webhook verification
        try:
            client.utility.verify_webhook_signature(
                data=request.body.decode('utf-8'),
                signature=razorpay_signature,
                secret=razorpay_key_secret
            )
        except Exception as e:
            # Handle verification failure
            return JsonResponse({'status': 'error', 'message': 'Webhook verification failed'})

        # Fetch the order details from Razorpay (replace with your actual order ID)
        order = client.order.fetch(razorpay_order_id)

        # Extract the plan information from the order notes
        plan_info = order['notes']['plan']
        points_plan = int(plan_info.split()[0])  # Extract the numeric part

        # Update the user's skill points in the SkillPoints model
        skill_points, created = SkillPoints.objects.get_or_create(user=request.user)
        skill_points.available_points += points_plan
        skill_points.save()

        # Create a SkillPointsTransaction entry
        SkillPointsTransaction.objects.create(
            sender=request.user,
            skill_points=points_plan,
            status='completed',
        )

        return JsonResponse({'status': 'success', 'message': 'Skill points added successfully'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})
