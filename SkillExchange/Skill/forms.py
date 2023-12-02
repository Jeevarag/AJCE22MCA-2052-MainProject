from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import CustomUser
from .models import UserSkill
from .models import UserLocation
from .models import Review
from .models import SkillPointRequest


class UserLocationForm(forms.ModelForm):
    class Meta:
        model = UserLocation
        fields = ('country', 'state', 'city')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = (
            'profile_picture',
            'about_me',
        )

class SkillForm(forms.ModelForm):
    class Meta:
        model = UserSkill
        fields = ['name', 'description']


class UserSearchForm(forms.Form):
    query = forms.CharField(label='Skill', max_length=100)
    

class SkillSessionForm(forms.Form):
    date_and_time = forms.DateTimeField(label='Date and Time', input_formats=['%Y-%m-%dT%H:%M'], widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    duration_minutes = forms.IntegerField(label='Duration (minutes)')

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text']


class SkillPointRequestForm(forms.ModelForm):
    class Meta:
        model = SkillPointRequest
        fields = ['points_requested']