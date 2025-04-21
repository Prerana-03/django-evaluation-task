from django.contrib import admin
from .models import AndroidApp, UserProfile, TaskCompletion

@admin.register(AndroidApp)
class AndroidAppAdmin(admin.ModelAdmin):
    list_display = ('name', 'package_name', 'points', 'created_at')
    search_fields = ('name', 'package_name')
    list_filter = ('points',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_points', 'created_at')
    search_fields = ('user__username', 'user__email')
    list_filter = ('total_points',)


@admin.register(TaskCompletion)
class TaskCompletionAdmin(admin.ModelAdmin):
    list_display = ('user', 'app', 'status', 'points_earned', 'submitted_at')
    search_fields = ('user__username', 'app__name')
    list_filter = ('status', 'submitted_at')
    readonly_fields = ('submitted_at', 'reviewed_at')
