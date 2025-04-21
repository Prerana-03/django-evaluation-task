from rest_framework import serializers
from django.contrib.auth.models import User
from core.models import AndroidApp, UserProfile, TaskCompletion


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff']
        read_only_fields = ['is_staff']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'total_points', 'bio', 'avatar', 'created_at', 'updated_at']
        read_only_fields = ['total_points', 'created_at', 'updated_at']


class AndroidAppSerializer(serializers.ModelSerializer):
    """Serializer for AndroidApp model"""
    class Meta:
        model = AndroidApp
        fields = ['id', 'name', 'package_name', 'description', 'points', 
                 'icon_url', 'app_url', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class TaskCompletionSerializer(serializers.ModelSerializer):
    """Serializer for TaskCompletion model"""
    username = serializers.CharField(source='user.username', read_only=True)
    app_name = serializers.CharField(source='app.name', read_only=True)
    
    class Meta:
        model = TaskCompletion
        fields = ['id', 'username', 'app_name', 'app', 'screenshot', 'status', 
                 'points_earned', 'admin_notes', 'submitted_at', 'reviewed_at']
        read_only_fields = ['status', 'points_earned', 'admin_notes', 'submitted_at', 'reviewed_at']


class TaskCompletionDetailSerializer(TaskCompletionSerializer):
    """Detailed serializer for TaskCompletion model"""
    app = AndroidAppSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta(TaskCompletionSerializer.Meta):
        fields = TaskCompletionSerializer.Meta.fields + ['user']
        read_only_fields = TaskCompletionSerializer.Meta.read_only_fields


class TaskCompletionAdminSerializer(serializers.ModelSerializer):
    """Serializer for administrators to approve/reject tasks"""
    class Meta:
        model = TaskCompletion
        fields = ['id', 'status', 'admin_notes']
        read_only_fields = ['id']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords don't match"})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        
        # Create a profile for the user
        UserProfile.objects.create(user=user)
        
        return user
