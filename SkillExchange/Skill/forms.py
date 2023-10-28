from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import CustomUser
from .models import UserSkill

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = (
            'profile_picture',
            'city',
            'about_me',
        )

class SkillForm(forms.ModelForm):
    class Meta:
        model = UserSkill
        fields = ['name', 'description']

class UserSearchForm(forms.Form):
    query = forms.CharField(label='Skill', max_length=100)


