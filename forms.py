from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, TextAreaField, IntegerField, URLField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, URL, ValidationError
from models import User


class LoginForm(FlaskForm):
    """Form for user login"""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class SignupForm(FlaskForm):
    """Form for user registration"""
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=20, message='Username must be between 3 and 20 characters')
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address')
    ])
    first_name = StringField('First Name', validators=[
        DataRequired(),
        Length(min=1, max=30, message='First name must be between 1 and 30 characters')
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(),
        Length(min=1, max=30, message='Last name must be between 1 and 30 characters')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        """Validate username is not already taken"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken')
    
    def validate_email(self, email):
        """Validate email is not already registered"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered')


class ProfileForm(FlaskForm):
    """Form for editing user profile"""
    bio = TextAreaField('Bio')
    avatar = FileField('Profile Picture', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    submit = SubmitField('Update Profile')


class AndroidAppForm(FlaskForm):
    """Form for creating and editing Android apps"""
    name = StringField('App Name', validators=[
        DataRequired(),
        Length(min=3, max=100, message='App name must be between 3 and 100 characters')
    ])
    package_name = StringField('Package Name', validators=[
        DataRequired(),
        Length(min=3, max=100, message='Package name must be between 3 and 100 characters')
    ])
    description = TextAreaField('Description', validators=[
        DataRequired(),
        Length(min=10, message='Description must be at least 10 characters')
    ])
    points = IntegerField('Points', validators=[
        DataRequired(),
        NumberRange(min=1, message='Points must be at least 1')
    ])
    icon_url = URLField('Icon URL', validators=[URL()])
    app_url = URLField('App URL', validators=[
        DataRequired(),
        URL(message='Please enter a valid URL')
    ])
    submit = SubmitField('Save App')


class TaskCompletionForm(FlaskForm):
    """Form for submitting task completion with screenshot"""
    screenshot = FileField('Screenshot', validators=[
        FileRequired('Please upload a screenshot'),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    submit = SubmitField('Submit Task')