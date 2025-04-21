from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator


class AndroidApp(models.Model):
    """Model for Android apps that users can download for points"""
    name = models.CharField(max_length=255)
    package_name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    points = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.points} points)"
    
    class Meta:
        ordering = ['-points', 'name']


class UserProfile(models.Model):
    """Extended user profile for tracking points and additional info"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    total_points = models.PositiveIntegerField(default=0)
    bio = models.TextField(blank=True)
    avatar = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


class TaskCompletion(models.Model):
    """Records when a user completes an app download task"""
    STATUS_CHOICES = (
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_completions')
    app = models.ForeignKey(AndroidApp, on_delete=models.CASCADE, related_name='completions')
    screenshot = models.ImageField(upload_to='screenshots/%Y/%m/%d/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='approved')
    points_earned = models.PositiveIntegerField(default=0)
    admin_notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.app.name} - {self.status}"
    
    def approve(self, admin_user):
        """Approve the task completion and award points to the user"""
        if self.status != 'approved':  # Only process if not already approved
            self.status = 'approved'
            self.points_earned = self.app.points
            self.reviewed_at = timezone.now()
            self.admin_notes = f"Approved by {admin_user.username} on {timezone.now()}"
            self.save()
            
            # Update user's total points
            profile = self.user.profile
            profile.total_points += self.points_earned
            profile.save()
            
            return True
        return False
    
    def reject(self, admin_user, reason=""):
        """Reject the task completion"""
        if self.status != 'rejected':  # Only process if not already rejected
            self.status = 'rejected'
            self.reviewed_at = timezone.now()
            self.admin_notes = f"Rejected by {admin_user.username} on {timezone.now()}. Reason: {reason}"
            self.save()
            return True
        return False
    
    class Meta:
        ordering = ['-submitted_at']
        unique_together = ['user', 'app']  # A user can only complete a specific app task once
