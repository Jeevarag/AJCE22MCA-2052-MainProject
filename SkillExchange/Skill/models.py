from django.db import models
from django.db.models import Q
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(
        upload_to='profile_pictures/', null=True, blank=True)
    about_me = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.username

    def followers_count(self):
        return Follower.objects.filter(Q(following=self) & Q(is_following=True)).count()

    def following_count(self):
        return Follower.objects.filter(follower=self, is_following=True).count()


class UserLocation(models.Model):
    # Link the location to the user
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    country = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)


class UserSkill(models.Model):
    class SkillCategory(models.TextChoices):
        ART_AND_DESIGN = 'Art and Design', 'Art and Design'
        SCIENCE_AND_TECHNOLOGY = 'Science and Technology', 'Science and Technology'
        CULINARY_ARTS = 'Culinary Arts', 'Culinary Arts'
        MUSIC_AND_PERFORMING_ARTS = 'Music and Performing Arts', 'Music and Performing Arts'
        LANGUAGE_AND_COMMUNICATION = 'Language and Communication', 'Language and Communication'
        FITNESS_AND_WELLNESS = 'Fitness and Wellness', 'Fitness and Wellness'
        CRAFTSMANSHIP = 'Craftsmanship', 'Craftsmanship'
        TECHNOLOGY_AND_IT = 'Technology and IT', 'Technology and IT',
        SPORTS_AND_RECREATION = 'Sports and Recreation', 'Sports and Recreation'
        HISTORY_AND_HUMANITIES = 'History and Humanities', 'History and Humanities'
        PARENTING_AND_FAMILY = 'Parenting and Family', 'Parenting and Family'
        MINDFULNESS_AND_WELLBEING = 'Mindfulness and Well-being', 'Mindfulness and Well-being'

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(
        max_length=50,
        choices=SkillCategory.choices,
        default=SkillCategory.ART_AND_DESIGN
    )

    def __str__(self):
        return self.name


class PreferredSkill(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='preferred_skills')
    skill = models.CharField(max_length=255)

    def __str__(self):
        return self.skill


class Follower(models.Model):
    follower = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='following')
    is_following = models.BooleanField(default=False)
    following = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.follower} is following {self.following}'


class Notification(models.Model):
    recipient = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification to {self.recipient.username}: {self.message}"


class SkillRequest(models.Model):
    sender = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="sent_requests")
    receiver = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="received_requests")
    message = models.TextField()
    status = models.CharField(max_length=10, choices=[(
        'pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')])

    def __str__(self):
        return f"Skill Request from {self.sender} to {self.receiver} for {self.skill.name}"


class SkillSession(models.Model):
    skill_request = models.ForeignKey(
        'SkillRequest', on_delete=models.CASCADE, related_name='skill_sessions')
    date_and_time = models.DateTimeField()
    duration_minutes = models.IntegerField()
    sender_status = models.CharField(max_length=20, choices=[(
        'attended', 'Attended'), ('absent', 'Absent')], blank=True, null=True)
    receiver_status = models.CharField(max_length=20, choices=[(
        'attended', 'Attended'), ('absent', 'Absent')], blank=True, null=True)
    status = models.CharField(max_length=20, choices=[(
        'scheduled', 'Scheduled'), ('completed', 'Completed')], default='scheduled')

    def __str__(self):
        return f"Skill Session for {self.skill_request.skill.name} with {self.skill_request.sender.username}"


class Review(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_reviews')
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_reviews')
    skill_session = models.ForeignKey(
        SkillSession, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review from {self.sender} to {self.receiver}'


class SkillPoints(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name='skill_points')
    available_points = models.IntegerField(default=0)
    spent_points = models.IntegerField(default=0)
    received_points = models.IntegerField(default=0)

    def __str__(self):
        return f"SkillPoints for {self.user.username}"


class SkillPointsTransaction(models.Model):
    sender = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='sent_transactions')
    receiver = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='received_transactions')
    skill_points = models.IntegerField()
    status = models.CharField(max_length=20, choices=[(
        'pending', 'Pending'), ('completed', 'Completed')], default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} sent {self.skill_points} skill points to {self.receiver.username} on {self.timestamp}"


class SkillPointsTransactionHistory(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='transaction_history')
    skill_points = models.IntegerField()
    amount_paid = models.FloatField()
    purchase_time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Transaction for {self.skill_points} skill points by {self.user.username} at {self.purchase_time}"


class SkillPointRequest(models.Model):
    sender = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='sent_skill_point_requests')
    receiver = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='received_skill_point_requests')
    points_requested = models.IntegerField()
    skill_request = models.ForeignKey(
        SkillRequest, on_delete=models.CASCADE, related_name='skill_point_requests')
    status_choices = [('pending', 'Pending'), ('accepted',
                                               'Accepted'), ('rejected', 'Rejected')]
    status = models.CharField(
        max_length=10, choices=status_choices, default='pending')

    def __str__(self):
        return f"SkillPointRequest from {self.sender.username} to {self.receiver.username} ({self.get_status_display()})"


class CollabRequest(models.Model):
    sender = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="sent_collab_requests")
    receiver = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="received_collab_requests")
    status = models.CharField(max_length=10, choices=[(
        'pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected')])

    def __str__(self):
        return f"Collab Request from {self.sender} to {self.receiver}"


class CollabSession(models.Model):
    collab_request = models.ForeignKey(
        'CollabRequest', on_delete=models.CASCADE, related_name='collab_sessions')
    date_and_time = models.DateTimeField()
    sender_status = models.CharField(max_length=20, choices=[(
        'attended', 'Attended'), ('absent', 'Absent')], blank=True, null=True)
    receiver_status = models.CharField(max_length=20, choices=[(
        'attended', 'Attended'), ('absent', 'Absent')], blank=True, null=True)
    status = models.CharField(max_length=20, choices=[(
        'scheduled', 'Scheduled'), ('completed', 'Completed')], default='scheduled')

    def __str__(self):
        return f"Collab Session for {self.collab_request.skill.name} with {self.collab_request.sender.username}"


class Message(models.Model):
    sender = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"


class Community(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    leader = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='led_community', null=True, blank=True)
    members = models.ManyToManyField(CustomUser, related_name='joined_communities')
    profile_picture = models.ImageField(upload_to='community_profile_pictures/', null=True, blank=True)

    def __str__(self):
        return self.name
