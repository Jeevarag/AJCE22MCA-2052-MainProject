from django.contrib import admin
from .models import CustomUser, UserSkill, UserLocation

# Register your models here.
class UserDetailsAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'about_me')

    def get_queryset(self, request):
        # Get the original queryset
        queryset = super(UserDetailsAdmin, self).get_queryset(request)

        # Filter out superusers
        queryset = queryset.filter(is_superuser=False)

        return queryset

class SkillDetailsAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

admin.site.register(CustomUser, UserDetailsAdmin)
admin.site.register(UserSkill, SkillDetailsAdmin)
