from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from core.models import AndroidApp, UserProfile, TaskCompletion
from .serializers import (
    UserSerializer, UserProfileSerializer, AndroidAppSerializer,
    TaskCompletionSerializer, TaskCompletionDetailSerializer,
    TaskCompletionAdminSerializer, UserRegistrationSerializer
)


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission to allow only admin users to modify objects
    """
    def has_permission(self, request, view):
        # Allow GET, HEAD, OPTIONS for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        # Allow write permissions only for admin users
        return request.user.is_staff


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for users
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    
    def get_permissions(self):
        """
        Allow registration for anyone, but only admin can see user list
        """
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        """
        Create a new user with profile
        """
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """
        Get current user info
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user profiles
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Regular users can only see their own profile, admins can see all
        """
        if self.request.user.is_staff:
            return UserProfile.objects.all()
        return UserProfile.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_profile(self, request):
        """
        Get current user's profile
        """
        profile = get_object_or_404(UserProfile, user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)


class AndroidAppViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Android apps
    """
    queryset = AndroidApp.objects.all()
    serializer_class = AndroidAppSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'package_name', 'description']
    ordering_fields = ['name', 'points', 'created_at']


class TaskCompletionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for task completions
    """
    queryset = TaskCompletion.objects.all()
    serializer_class = TaskCompletionSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['submitted_at', 'status']
    
    def get_queryset(self):
        """
        Regular users can only see their own submissions, admins can see all
        """
        if self.request.user.is_staff:
            return TaskCompletion.objects.all()
        return TaskCompletion.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """
        Use different serializers based on the action
        """
        if self.action == 'retrieve':
            return TaskCompletionDetailSerializer
        if self.action in ['approve', 'reject']:
            return TaskCompletionAdminSerializer
        return TaskCompletionSerializer
    
    def perform_create(self, serializer):
        """
        Set the current user and initial status when creating a submission
        """
        app_id = self.request.data.get('app')
        app = get_object_or_404(AndroidApp, pk=app_id)
        
        serializer.save(
            user=self.request.user,
            status='pending',
        )
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        """
        Approve a task completion
        """
        task = self.get_object()
        task.approve(request.user)
        
        serializer = self.get_serializer(task)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def reject(self, request, pk=None):
        """
        Reject a task completion
        """
        task = self.get_object()
        reason = request.data.get('admin_notes', '')
        task.reject(request.user, reason)
        
        serializer = self.get_serializer(task)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """
        Get all pending task completions (admin only)
        """
        if not request.user.is_staff:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        pending_tasks = TaskCompletion.objects.filter(status='pending')
        serializer = self.get_serializer(pending_tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """
        Get current user's task completions
        """
        tasks = TaskCompletion.objects.filter(user=request.user)
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
