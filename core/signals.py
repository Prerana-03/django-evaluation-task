from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, TaskCompletion


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create a UserProfile automatically when a new User is created.
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=TaskCompletion)
def update_profile_points(sender, instance, **kwargs):
    """
    Update the user's total points when a task is approved.
    """
    if instance.status == 'approved' and instance.points_earned > 0:
        # Get the user's profile
        profile = instance.user.profile
        
        # Add the points earned to the total
        profile.total_points += instance.points_earned
        
        # Save the profile
        profile.save()
