from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .models import Member, Admin, Event
from . import db
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import re
import logging
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask-Limiter
auth = Blueprint('auth', __name__)
limiter = Limiter(key_func=get_remote_address)

class Config:
    MAX_ADMINS = 2
    PHONE_NUMBER_REGEX = r'^\+?\d{10,15}$'
    TEMPLATES = {
        'landing': 'about.html',
        'get_started': 'base.html',
        'login': 'login.html',
        'sign_up': 'sign_up.html',
        'add_event': 'add_event.html',
        'admin_login': 'admin_login.html',
        'admin_signup': 'admin_signup.html',
        'admin_activities': 'admin_activities.html',
        'manage_members': 'manage_members.html',
        'manage_events': 'manage_events.html',
        'edit_member': 'edit_member.html',
        'edit_event': 'edit_event.html',
        'member_dashboard': 'member_dashboard.html',
        'view_events': 'view_events.html',
        'view_readings': 'view_readings.html'
    }

def is_valid_phone(phone):
    return bool(re.match(Config.PHONE_NUMBER_REGEX, phone))

def commit_to_db(obj):
    try:
        db.session.add(obj)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        logger.error(f"Database error: {str(e)}")
        flash('A database error occurred. Please try again.', 'error')
        return False

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(current_user, 'is_admin', False):
            flash('Admin access required', 'error')
            return redirect(url_for('auth.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@auth.route('/')
def landing_page():
    return render_template(Config.TEMPLATES['landing'])

@auth.route('/get_started')
def get_started():
    return render_template(Config.TEMPLATES['get_started'])

@auth.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated and not getattr(current_user, 'is_admin', False):
        return redirect(url_for('auth.member_dashboard'))

    if request.method == 'POST':
        zaq_number = request.form.get('zaq_number', '').strip()
        phone_number = request.form.get('phone_number', '').strip()

        if not zaq_number or not phone_number:
            flash('Both fields are required', 'error')
        elif not is_valid_phone(phone_number):
            flash('Invalid phone number format', 'error')
        else:
            member = Member.query.filter_by(zaq_number=zaq_number).first()
            if member and member.phone_number == phone_number:
                login_user(member, remember=True)
                logger.info(f"Member login: {zaq_number}")
                flash('Login successful!', 'success')
                return redirect(url_for('auth.member_dashboard'))
            else:
                logger.warning(f"Failed login: {zaq_number}")
                flash('Invalid credentials', 'error')

    return render_template(Config.TEMPLATES['login'])

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'info')
    return redirect(url_for('auth.login'))

@auth.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        form_data = {
            'full_name': request.form.get('full_name', '').strip(),
            'zaq_number': request.form.get('zaq_number', '').strip(),
            'phone_number': request.form.get('phone_number', '').strip(),
            'jumuiya': request.form.get('jumuiya', '').strip(),
            'outstation': request.form.get('outstation', '').strip(),
            'center': request.form.get('center', '').strip(),
            'zone': request.form.get('zone', '').strip()
        }

        required_fields = ['full_name', 'zaq_number', 'phone_number']
        if not all(form_data[field] for field in required_fields):
            flash('Missing required fields', 'error')
        elif not is_valid_phone(form_data['phone_number']):
            flash('Invalid phone number format', 'error')
        elif Member.query.filter_by(zaq_number=form_data['zaq_number']).first():
            flash('ZAQ number already registered', 'error')
        else:
            new_member = Member(**form_data)
            if commit_to_db(new_member):
                flash('Registration successful! Please login', 'success')
                return redirect(url_for('auth.login'))
                
    return render_template(Config.TEMPLATES['sign_up'])

@auth.route('/member_dashboard')
@login_required
def member_dashboard():
    if getattr(current_user, 'is_admin', False):
        return redirect(url_for('auth.admin_dashboard'))
    
    upcoming_events = Event.query.filter(
        Event.date >= datetime.now()
    ).order_by(Event.date).limit(5).all()
    
    return render_template(Config.TEMPLATES['member_dashboard'], events=upcoming_events)

@auth.route('/admin_login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def admin_login():
    if current_user.is_authenticated and getattr(current_user, 'is_admin', False):
        return redirect(url_for('auth.admin_dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        admin = Admin.query.filter_by(email=email).first()
        if admin and check_password_hash(admin.password, password) and admin.is_admin:
            login_user(admin, remember=True)
            logger.info(f"Admin login: {email}")
            flash('Admin login successful!', 'success')
            return redirect(url_for('auth.admin_dashboard'))
        else:
            logger.warning(f"Failed admin login: {email}")
            flash('Invalid credentials', 'error')

    return render_template(Config.TEMPLATES['admin_login'])

@auth.route('/admin_signup', methods=['GET', 'POST'])
def admin_signup():
    if current_user.is_authenticated and getattr(current_user, 'is_admin', False):
        return redirect(url_for('auth.admin_dashboard'))

    if request.method == 'POST':
        form_data = {
            'full_name': request.form.get('full_name', '').strip(),
            'email': request.form.get('email', '').strip(),
            'phone_number': request.form.get('phone_number', '').strip(),
            'password': request.form.get('password', ''),
            'confirm_password': request.form.get('confirm_password', '')
        }

        if not all(form_data.values()):
            flash('All fields are required', 'error')
        elif form_data['password'] != form_data['confirm_password']:
            flash('Passwords do not match', 'error')
        elif not is_valid_phone(form_data['phone_number']):
            flash('Invalid phone number format', 'error')
        elif Admin.query.count() >= Config.MAX_ADMINS:
            flash(f'Maximum {Config.MAX_ADMINS} admins allowed', 'error')
        elif Admin.query.filter_by(email=form_data['email']).first():
            flash('Email already registered', 'error')
        else:
            hashed_password = generate_password_hash(form_data['password'], method='pbkdf2:sha256')
            new_admin = Admin(
                full_name=form_data['full_name'],
                email=form_data['email'],
                phone_number=form_data['phone_number'],
                password=hashed_password,
                is_admin=True
            )
            if commit_to_db(new_admin):
                flash('Admin account created! Please login', 'success')
                return redirect(url_for('auth.admin_login'))
                
    return render_template(Config.TEMPLATES['admin_signup'])

@auth.route('/admin_dashboard')
@admin_required
def admin_dashboard():
    stats = {
        'members': Member.query.count(),
        'events': Event.query.count(),
        'recent_members': Member.query.order_by(
            Member.date_joined.desc()
        ).limit(5).all()
    }
    return render_template(Config.TEMPLATES['admin_activities'], stats=stats)

@auth.route('/admin_logout')
@admin_required
def admin_logout():
    logout_user()
    flash('Admin logged out', 'info')
    return redirect(url_for('auth.admin_login'))

@auth.route('/manage_members')
@admin_required
def manage_members():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    
    query = Member.query
    if search:
        query = query.filter(
            Member.full_name.ilike(f'%{search}%') | 
            Member.zaq_number.ilike(f'%{search}%')
        )
    
    members = query.order_by(
        Member.outstation
    ).paginate(page=page, per_page=20)
    
    return render_template(Config.TEMPLATES['manage_members'], members=members)

@auth.route('/add_event', methods=['GET', 'POST'])
@admin_required
def add_event():
    if request.method == 'POST':
        try:
            event = Event(
                title=request.form.get('title', '').strip(),
                theme=request.form.get('theme', '').strip(),
                involved=request.form.get('involved', '').strip(),
                venue=request.form.get('venue', '').strip(),
                date=datetime.strptime(request.form.get('date'), '%Y-%m-%d'),
                admin_id=current_user.id
            )
            if commit_to_db(event):
                flash('Event added successfully', 'success')
                return redirect(url_for('auth.manage_events'))
        except ValueError:
            flash('Invalid date format', 'error')
        except Exception as e:
            logger.error(f"Event creation error: {str(e)}")
            flash('Error creating event', 'error')
    
    return render_template(Config.TEMPLATES['add_event'])

@auth.route('/manage_events')
@admin_required
def manage_events():
    events = Event.query.order_by(Event.date.desc()).all()
    return render_template(Config.TEMPLATES['manage_events'], events=events)

@auth.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
@admin_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    
    if request.method == 'POST':
        try:
            event.title = request.form.get('title', '').strip()
            event.theme = request.form.get('theme', '').strip()
            event.involved = request.form.get('involved', '').strip()
            event.venue = request.form.get('venue', '').strip()
            event.date = datetime.strptime(request.form.get('date'), '%Y-%m-%d')
            db.session.commit()
            flash('Event updated successfully', 'success')
            return redirect(url_for('auth.manage_events'))
        except ValueError:
            flash('Invalid date format', 'error')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Event update error: {str(e)}")
            flash('Error updating event', 'error')
    
    return render_template(Config.TEMPLATES['edit_event'], event=event)

@auth.route('/delete_event/<int:event_id>', methods=['POST'])
@admin_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    try:
        db.session.delete(event)
        db.session.commit()
        flash('Event deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Event deletion error: {str(e)}")
        flash('Error deleting event', 'error')
    return redirect(url_for('auth.manage_events'))

@auth.route('/view_events')
@login_required
def view_events():
    events = Event.query.order_by(Event.date).all()
    return render_template(Config.TEMPLATES['view_events'], events=events)

@auth.route('/view_readings')
@login_required
def view_readings():
    return render_template(Config.TEMPLATES['view_readings'])