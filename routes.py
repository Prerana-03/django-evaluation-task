import os
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, session, jsonify, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from app import app, db
from models import User, UserProfile, AndroidApp, TaskCompletion
from forms import LoginForm, SignupForm, ProfileForm, AndroidAppForm, TaskCompletionForm

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Configure upload folder
UPLOAD_FOLDER = os.path.join(app.root_path, 'static/uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Utility function to save uploaded files
def save_file(file, subfolder='screenshots'):
    filename = secure_filename(file.filename)
    # Create a unique filename to prevent overwriting
    unique_filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
    
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], subfolder)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
    file_path = os.path.join(folder_path, unique_filename)
    file.save(file_path)
    
    # Return the relative path for storing in the database
    return f"uploads/{subfolder}/{unique_filename}"

# Home page
@app.route('/')
def home():
    """Homepage route"""
    # Get some stats for the home page
    num_apps = AndroidApp.query.count()
    num_users = User.query.count()
    
    # Get top users by points
    top_users = db.session.query(
        User, UserProfile
    ).join(UserProfile).order_by(
        UserProfile.total_points.desc()
    ).limit(5).all()
    
    return render_template('home.html', 
                          num_apps=num_apps, 
                          num_users=num_users,
                          top_users=top_users)

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login route"""
    form = LoginForm()
    
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """Logout route"""
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration route"""
    form = SignupForm()
    
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if form.validate_on_submit():
        # Check if username or email already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already taken', 'danger')
            return render_template('signup.html', form=form)
            
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered', 'danger')
            return render_template('signup.html', form=form)
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        user.set_password(form.password.data)
        
        # Create user profile
        profile = UserProfile(user=user)
        
        # Add to database
        db.session.add(user)
        db.session.add(profile)
        db.session.commit()
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html', form=form)

# User Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing earned points and completed tasks"""
    # Get user profile
    profile = current_user.profile
    
    # Get user's task completions
    task_completions = TaskCompletion.query.filter_by(user_id=current_user.id).all()
    
    # Get available apps (exclude already completed ones)
    completed_app_ids = [tc.app_id for tc in task_completions]
    available_apps = AndroidApp.query.filter(~AndroidApp.id.in_(completed_app_ids) if completed_app_ids else True).all()
    
    return render_template('dashboard.html', 
                          profile=profile,
                          task_completions=task_completions,
                          available_apps=available_apps)

# User Profile
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """View and edit user profile"""
    profile = current_user.profile
    form = ProfileForm(obj=profile)
    
    if form.validate_on_submit():
        if form.avatar.data:
            file_path = save_file(form.avatar.data, 'avatars')
            profile.avatar = file_path
            
        profile.bio = form.bio.data
        db.session.commit()
        
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('profile.html', profile=profile, form=form)

# App details and task submission
@app.route('/apps/<int:app_id>', methods=['GET', 'POST'])
@login_required
def app_detail(app_id):
    """View app details and submit task completion"""
    app = AndroidApp.query.get_or_404(app_id)
    form = TaskCompletionForm()
    
    # Check if user already completed this task
    existing_task = TaskCompletion.query.filter_by(
        user_id=current_user.id, app_id=app_id
    ).first()
    
    if existing_task:
        flash('You have already submitted a completion for this app', 'warning')
        return redirect(url_for('dashboard'))
    
    if form.validate_on_submit():
        if form.screenshot.data:
            file_path = save_file(form.screenshot.data, 'screenshots')
            
            # Create task completion
            task_completion = TaskCompletion(
                user_id=current_user.id,
                app_id=app_id,
                screenshot=file_path,
                status='pending'
            )
            
            db.session.add(task_completion)
            db.session.commit()
            
            flash('Task submitted successfully! Awaiting approval.', 'success')
            return redirect(url_for('dashboard'))
    
    return render_template('app_detail.html', app=app, form=form)

# Admin routes
@app.route('/admin')
@login_required
def admin_dashboard():
    """Admin dashboard"""
    if not current_user.is_admin:
        flash('You do not have admin privileges', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get platform stats
    num_users = User.query.count()
    num_apps = AndroidApp.query.count()
    num_pending = TaskCompletion.query.filter_by(status='pending').count()
    num_approved = TaskCompletion.query.filter_by(status='approved').count()
    
    # Get recent task completions
    recent_tasks = TaskCompletion.query.order_by(TaskCompletion.submitted_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html',
                          num_users=num_users,
                          num_apps=num_apps,
                          num_pending=num_pending,
                          num_approved=num_approved,
                          recent_tasks=recent_tasks)

@app.route('/admin/apps')
@login_required
def admin_apps():
    """List of all Android apps (admin view)"""
    if not current_user.is_admin:
        flash('You do not have admin privileges', 'danger')
        return redirect(url_for('dashboard'))
    
    apps = AndroidApp.query.all()
    return render_template('admin/apps.html', apps=apps)

@app.route('/admin/apps/add', methods=['GET', 'POST'])
@login_required
def admin_add_app():
    """Add new Android app"""
    if not current_user.is_admin:
        flash('You do not have admin privileges', 'danger')
        return redirect(url_for('dashboard'))
    
    form = AndroidAppForm()
    
    if form.validate_on_submit():
        app = AndroidApp(
            name=form.name.data,
            package_name=form.package_name.data,
            description=form.description.data,
            points=form.points.data,
            icon_url=form.icon_url.data,
            app_url=form.app_url.data
        )
        
        db.session.add(app)
        db.session.commit()
        
        flash('App added successfully!', 'success')
        return redirect(url_for('admin_apps'))
    
    return render_template('admin/app_form.html', form=form, title='Add New App')

@app.route('/admin/apps/edit/<int:app_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_app(app_id):
    """Edit existing Android app"""
    if not current_user.is_admin:
        flash('You do not have admin privileges', 'danger')
        return redirect(url_for('dashboard'))
    
    app = AndroidApp.query.get_or_404(app_id)
    form = AndroidAppForm(obj=app)
    
    if form.validate_on_submit():
        app.name = form.name.data
        app.package_name = form.package_name.data
        app.description = form.description.data
        app.points = form.points.data
        app.icon_url = form.icon_url.data
        app.app_url = form.app_url.data
        
        db.session.commit()
        
        flash('App updated successfully!', 'success')
        return redirect(url_for('admin_apps'))
    
    return render_template('admin/app_form.html', form=form, title='Edit App')

@app.route('/admin/apps/delete/<int:app_id>', methods=['POST'])
@login_required
def admin_delete_app(app_id):
    """Delete Android app"""
    if not current_user.is_admin:
        flash('You do not have admin privileges', 'danger')
        return redirect(url_for('dashboard'))
    
    app = AndroidApp.query.get_or_404(app_id)
    
    db.session.delete(app)
    db.session.commit()
    
    flash('App deleted successfully!', 'success')
    return redirect(url_for('admin_apps'))

@app.route('/admin/tasks')
@login_required
def admin_tasks():
    """View all task submissions (admin view)"""
    if not current_user.is_admin:
        flash('You do not have admin privileges', 'danger')
        return redirect(url_for('dashboard'))
    
    tasks = TaskCompletion.query.order_by(TaskCompletion.submitted_at.desc()).all()
    return render_template('admin/tasks.html', tasks=tasks)

@app.route('/admin/tasks/pending')
@login_required
def admin_pending_tasks():
    """View pending task submissions (admin view)"""
    if not current_user.is_admin:
        flash('You do not have admin privileges', 'danger')
        return redirect(url_for('dashboard'))
    
    tasks = TaskCompletion.query.filter_by(status='pending').order_by(TaskCompletion.submitted_at.desc()).all()
    return render_template('admin/tasks.html', tasks=tasks, title='Pending Tasks')

@app.route('/admin/tasks/review/<int:task_id>')
@login_required
def admin_review_task(task_id):
    """Review task submission"""
    if not current_user.is_admin:
        flash('You do not have admin privileges', 'danger')
        return redirect(url_for('dashboard'))
    
    task = TaskCompletion.query.get_or_404(task_id)
    return render_template('admin/review_task.html', task=task)

@app.route('/admin/tasks/approve/<int:task_id>', methods=['POST'])
@login_required
def admin_approve_task(task_id):
    """Approve task submission"""
    if not current_user.is_admin:
        flash('You do not have admin privileges', 'danger')
        return redirect(url_for('dashboard'))
    
    task = TaskCompletion.query.get_or_404(task_id)
    admin_notes = request.form.get('admin_notes', '')
    
    task.approve(admin_notes)
    db.session.commit()
    
    flash('Task approved successfully!', 'success')
    return redirect(url_for('admin_pending_tasks'))

@app.route('/admin/tasks/reject/<int:task_id>', methods=['POST'])
@login_required
def admin_reject_task(task_id):
    """Reject task submission"""
    if not current_user.is_admin:
        flash('You do not have admin privileges', 'danger')
        return redirect(url_for('dashboard'))
    
    task = TaskCompletion.query.get_or_404(task_id)
    admin_notes = request.form.get('admin_notes', '')
    
    task.reject(admin_notes)
    db.session.commit()
    
    flash('Task rejected successfully!', 'success')
    return redirect(url_for('admin_pending_tasks'))

@app.route('/admin/users')
@login_required
def admin_users():
    """View all users (admin view)"""
    if not current_user.is_admin:
        flash('You do not have admin privileges', 'danger')
        return redirect(url_for('dashboard'))
    
    users = User.query.all()
    return render_template('admin/users.html', users=users)

# Problem Set 1 route
@app.route('/problem-set-1')
def problem_set_1():
    """View for problem set 1"""
    # The text from Problem Set 1
    json_text = """{"orders":[{"id":1},{"id":2},{"id":3},{"id":4},{"id":5},{"id":6},{"id":7},{"id":8},{"id":9},{"id":10},{"id":11},{"id":648},{"id":649},{"id":650},{"id":651},{"id":652},{"id":653}],"errors":[{"code":3,"message":"[PHP Warning #2] count(): Parameter must be an array or an object that implements Countable (153)"}]}"""
    
    # Import the function
    from problem_set_1 import extract_orange_numbers
    
    # Extract the numbers
    result = extract_orange_numbers(json_text)
    
    return render_template('problem_set_1.html', 
                          json_text=json_text, 
                          result=result)