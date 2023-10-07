from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    about_me = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.username


class UserSkill(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name


