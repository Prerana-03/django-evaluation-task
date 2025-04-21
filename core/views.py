from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.contrib.auth import login, authenticate

from .models import AndroidApp, UserProfile, TaskCompletion
from .forms import UserProfileForm, TaskCompletionForm, AndroidAppForm


def home(request):
    """Homepage view"""
    apps_count = AndroidApp.objects.count()
    users_count = User.objects.count()
    points_awarded = UserProfile.objects.aggregate(total=Sum('total_points'))['total'] or 0
    
    context = {
        'apps_count': apps_count,
        'users_count': users_count,
        'points_awarded': points_awarded,
    }
    return render(request, 'home.html', context)


def signup(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            
            # Log the user in
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            
            return redirect('user_dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def user_dashboard(request):
    """User dashboard showing earned points and completed tasks"""
    user_profile = request.user.profile
    completed_tasks = TaskCompletion.objects.filter(user=request.user, status='approved')
    
    available_apps = AndroidApp.objects.exclude(
        completions__user=request.user,
        completions__status='approved'
    )
    
    context = {
        'profile': user_profile,
        'completed_tasks': completed_tasks,
        'available_apps': available_apps,
    }
    return render(request, 'user/dashboard.html', context)


@login_required
def user_profile(request):
    """View and edit user profile"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('user_profile')
    else:
        form = UserProfileForm(instance=request.user.profile)
    
    context = {
        'form': form,
        'profile': request.user.profile,
    }
    return render(request, 'user/profile.html', context)


@login_required
def task_detail(request, app_id):
    """View app details and submit task completion"""
    app = get_object_or_404(AndroidApp, pk=app_id)
    
    # Check if user has already completed this task
    existing_task = TaskCompletion.objects.filter(user=request.user, app=app).first()
    
    if request.method == 'POST':
        # User can only submit if they haven't already or if previous submission was rejected
        if existing_task and existing_task.status == 'approved':
            messages.error(request, 'You have already submitted this task')
            return redirect('task_detail', app_id=app_id)
        
        form = TaskCompletionForm(request.POST, request.FILES)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.app = app
            task.status = 'approved'
            task.points_earned = app.points
            task.save()
            
            # Update user's total points
            profile = request.user.profile
            profile.total_points += app.points
            profile.save()
            
            messages.success(request, 'Task submitted successfully!')
            return redirect('user_dashboard')
    else:
        form = TaskCompletionForm()
    
    context = {
        'app': app,
        'form': form,
        'existing_task': existing_task,
    }
    return render(request, 'user/task_detail.html', context)


# Admin views
@login_required
def admin_dashboard(request):
    """Admin dashboard"""
    if not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to access this page")
    
    total_apps = AndroidApp.objects.count()
    total_users = User.objects.filter(is_staff=False).count()
    
    context = {
        'total_apps': total_apps,
        'total_users': total_users,
    }
    return render(request, 'admin/dashboard.html', context)


@login_required
def admin_app_list(request):
    """List of all Android apps (admin view)"""
    if not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to access this page")
    
    apps = AndroidApp.objects.all()
    
    context = {
        'apps': apps,
    }
    return render(request, 'admin/app_list.html', context)


@login_required
def admin_app_form(request, app_id=None):
    """Create or edit an Android app"""
    if not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to access this page")
    
    if app_id:
        app = get_object_or_404(AndroidApp, pk=app_id)
        title = "Edit App"
    else:
        app = None
        title = "Add New App"
    
    if request.method == 'POST':
        form = AndroidAppForm(request.POST, instance=app)
        if form.is_valid():
            form.save()
            messages.success(request, f"App {'updated' if app_id else 'created'} successfully")
            return redirect('admin_app_list')
    else:
        form = AndroidAppForm(instance=app)
    
    context = {
        'form': form,
        'title': title,
        'app': app,
    }
    return render(request, 'admin/app_form.html', context)
