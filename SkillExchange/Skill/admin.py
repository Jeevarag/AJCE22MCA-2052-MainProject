from django.contrib import admin
from .models import CustomUser, UserSkill

# Register your models here.
class UserDetailsAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'city', 'about_me')

class SkillDetailsAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

admin.site.register(CustomUser, UserDetailsAdmin)
admin.site.register(UserSkill, SkillDetailsAdmin)