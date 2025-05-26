from flask import Blueprint, render_template, redirect, url_for, request, flash
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

# Config (assumed to be in config.py or hardcoded)
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

# Helper function for phone number validation
def is_valid_phone(phone):
    return bool(re.match(Config.PHONE_NUMBER_REGEX, phone))

# Helper function for member creation
def create_member(full_name, zaq_number, jumuiya, outstation, center, zone, phone_number, redirect_to='auth.login'):
    if not all([full_name, zaq_number, phone_number]):
        flash('Required fields must be filled!', category='error')
        return False, render_template(Config.TEMPLATES['sign_up'], user=current_user)

    if not is_valid_phone(phone_number):
        flash('Invalid phone number format.', category='error')
        return False, render_template(Config.TEMPLATES['sign_up'], user=current_user)

    if Member.query.filter_by(zaq_number=zaq_number).first():
        flash('ZAQ Number already exists!', category='error')
        return False, render_template(Config.TEMPLATES['sign_up'], user=current_user)

    new_member = Member(
        full_name=full_name, zaq_number=zaq_number, jumuiya=jumuiya,
        outstation=outstation, center=center, zone=zone, phone_number=phone_number
    )
    db.session.add(new_member)
    try:
        db.session.commit()
        flash('Member added successfully!', category='success')
        return True, redirect(url_for(redirect_to))
    except Exception:
        db.session.rollback()
        flash('An error occurred while adding the member.', category='error')
        return False, render_template(Config.TEMPLATES['sign_up'], user=current_user)

# Admin-only decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.__class__.__name__ != 'Admin':
            flash('Access denied. Admin privileges required.', category='error')
            return redirect(url_for('auth.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@auth.route('/', methods=['GET'])
def landing_page():
    """Render the landing page."""
    return render_template(Config.TEMPLATES['landing'])

@auth.route('/get_started', methods=['GET'])
def get_started():
    """Render the get started page."""
    return render_template(Config.TEMPLATES['get_started'])

@auth.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    """Handle member login with ZAQ number and phone number."""
    if request.method == 'POST':
        zaq_number = request.form.get('zaq_number', '').strip()
        phone_number = request.form.get('phone_number', '').strip()

        if not zaq_number or not phone_number:
            flash('ZAQ Number and phone number are required.', category='error')
            return render_template(Config.TEMPLATES['login'], user=current_user)

        if not is_valid_phone(phone_number):
            flash('Invalid phone number format.', category='error')
            return render_template(Config.TEMPLATES['login'], user=current_user)

        member = Member.query.filter_by(zaq_number=zaq_number).first()
        if member and member.phone_number == phone_number:
            login_user(member, remember=True)
            flash('Login successful!', category='success')
            return redirect(url_for('auth.member_dashboard'))
        else:
            logger.warning(f"Failed login attempt for ZAQ: {zaq_number}, Phone: {phone_number}")
            flash('Invalid ZAQ Number or phone number.', category='error')

    return render_template(Config.TEMPLATES['login'], user=current_user)

@auth.route('/logout', methods=['GET'])
def logout():
    """Handle member logout."""
    logout_user()
    flash('Logged out successfully!', category='info')
    return redirect(url_for('auth.login'))

@auth.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    """Handle member registration."""
    if request.method == 'POST':
        success, response = create_member(
            request.form.get('full_name'), request.form.get('zaq_number'),
            request.form.get('jumuiya'), request.form.get('outstation'),
            request.form.get('center'), request.form.get('zone'),
            request.form.get('phone_number'), redirect_to='auth.login'
        )
        return response
    return render_template(Config.TEMPLATES['sign_up'], user=current_user)

@auth.route('/admin_login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")  # Added for consistency
def admin_login():
    """Handle admin login with email and password."""
    if current_user.is_authenticated and current_user.__class__.__name__ == 'Admin':
        return redirect(url_for('auth.admin_activities'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Email and password are required.', category='error')
            return render_template(Config.TEMPLATES['admin_login'], user=current_user)

        admin = Admin.query.filter_by(email=email).first()
        if admin and check_password_hash(admin.password, password):
            login_user(admin, remember=True)
            flash('Admin login successful!', category='success')
            return redirect(url_for('auth.admin_activities'))
        else:
            logger.warning(f"Failed admin login attempt for email: {email}")
            flash('Invalid email or password.', category='error')

    return render_template(Config.TEMPLATES['admin_login'], user=current_user)

@auth.route('/admin_signup', methods=['GET', 'POST'])
def admin_signup():
    """Handle admin registration."""
    if current_user.is_authenticated and current_user.__class__.__name__ == 'Admin':
        return redirect(url_for('auth.admin_activities'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        phone_number = request.form.get('phone_number', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not all([full_name, email, phone_number, password, confirm_password]):
            flash('All fields are required.', category='error')
            return render_template(Config.TEMPLATES['admin_signup'], user=current_user)

        if password != confirm_password:
            flash('Passwords do not match!', category='error')
            return render_template(Config.TEMPLATES['admin_signup'], user=current_user)

        if not is_valid_phone(phone_number):
            flash('Invalid phone number format.', category='error')
            return render_template(Config.TEMPLATES['admin_signup'], user=current_user)

        admin_count = Admin.query.count()
        if admin_count >= Config.MAX_ADMINS:
            flash(f'Admin limit reached. Only {Config.MAX_ADMINS} admins allowed.', category='error')
            return render_template(Config.TEMPLATES['admin_signup'], user=current_user)

        existing_admin = Admin.query.filter_by(email=email).first()
        if existing_admin:
            flash('Email already exists!', category='error')
            return render_template(Config.TEMPLATES['admin_signup'], user=current_user)

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_admin = Admin(
            full_name=full_name, email=email,
            phone_number=phone_number, password=hashed_password
        )
        db.session.add(new_admin)
        try:
            db.session.commit()
            flash('Admin account created successfully! Please log in.', category='success')
            return redirect(url_for('auth.admin_login'))
        except Exception:
            db.session.rollback()
            flash('An error occurred while creating the admin account.', category='error')

    return render_template(Config.TEMPLATES['admin_signup'], user=current_user)

@auth.route('/admin_logout', methods=['GET'])
@login_required
@admin_required
def admin_logout():
    """Handle admin logout."""
    logout_user()
    flash('Admin logged out successfully!', category='info')
    return redirect(url_for('auth.admin_login'))

@auth.route('/admin_activities', methods=['GET'])
@login_required
@admin_required
def admin_activities():
    """Render admin activities dashboard."""
    return render_template(Config.TEMPLATES['admin_activities'], user=current_user)

@auth.route('/add_event', methods=['GET', 'POST'])
@login_required
@admin_required
def add_event():
    """Handle event creation."""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        theme = request.form.get('theme', '').strip()
        involved = request.form.get('involved', '').strip()
        venue = request.form.get('venue', '').strip()
        date_str = request.form.get('date', '').strip()

        if not all([title, theme, involved, venue, date_str]):
            flash('All fields are required!', category='error')
            return render_template(Config.TEMPLATES['add_event'], user=current_user)

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
            new_event = Event(
                title=title, theme=theme, involved=involved,
                venue=venue, date=date, user_id=None
            )
            db.session.add(new_event)
            db.session.commit()
            flash('Event added successfully!', category='success')
            return redirect(url_for('auth.manage_events'))
        except ValueError:
            flash('Invalid date format. Use YYYY-MM-DD.', category='error')
        except Exception:
            db.session.rollback()
            flash('An error occurred while adding the event.', category='error')

    return render_template(Config.TEMPLATES['add_event'], user=current_user)

@auth.route('/add_member', methods=['GET', 'POST'])
@login_required
@admin_required
def add_member():
    """Handle admin adding a new member."""
    if request.method == 'POST':
        success, response = create_member(
            request.form.get('full_name'), request.form.get('zaq_number'),
            request.form.get('jumuiya'), request.form.get('outstation'),
            request.form.get('center'), request.form.get('zone'),
            request.form.get('phone_number'), redirect_to='auth.admin_activities'
        )
        return response
    return render_template(Config.TEMPLATES['sign_up'], user=current_user)

@auth.route('/manage_members', methods=['GET'])
@login_required
@admin_required
def manage_members():
    """Handle member management with search, sort, and pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search_query = request.args.get('search', '').strip()
    sort_by = request.args.get('sort_by', 'outstation')

    query = Member.query
    if search_query:
        query = query.filter(Member.zaq_number.like(f"%{search_query}%"))
    query = query.order_by(Member.zone if sort_by == 'zone' else Member.outstation)
    members = query.paginate(page=page, per_page=per_page)

    outstation_counts = db.session.query(Member.outstation, db.func.count(Member.id)).group_by(Member.outstation).all()
    zone_counts = db.session.query(Member.zone, db.func.count(Member.id)).group_by(Member.zone).all()

    return render_template(
        Config.TEMPLATES['manage_members'], user=current_user, members=members,
        outstation_counts=outstation_counts, zone_counts=zone_counts,
        search_query=search_query, sort_by=sort_by
    )

@auth.route('/edit_member/<int:member_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_member(member_id):
    """Handle editing a member."""
    member = Member.query.get_or_404(member_id)

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        zaq_number = request.form.get('zaq_number', '').strip()
        jumuiya = request.form.get('jumuiya', '').strip()
        outstation = request.form.get('outstation', '').strip()
        center = request.form.get('center', '').strip()
        zone = request.form.get('zone', '').strip()
        phone_number = request.form.get('phone_number', '').strip()

        if not all([full_name, zaq_number, phone_number]):
            flash('Required fields must be filled!', category='error')
            return render_template(Config.TEMPLATES['edit_member'], member=member, user=current_user)

        if not is_valid_phone(phone_number):
            flash('Invalid phone number format.', category='error')
            return render_template(Config.TEMPLATES['edit_member'], member=member, user=current_user)

        existing_member = Member.query.filter_by(zaq_number=zaq_number).filter(Member.id != member_id).first()
        if existing_member:
            flash('ZAQ Number already exists!', category='error')
            return render_template(Config.TEMPLATES['edit_member'], member=member, user=current_user)

        member.full_name = full_name
        member.zaq_number = zaq_number
        member.jumuiya = jumuiya
        member.outstation = outstation
        member.center = center
        member.zone = zone
        member.phone_number = phone_number
        try:
            db.session.commit()
            flash('Member updated successfully!', category='success')
            return redirect(url_for('auth.manage_members'))
        except Exception:
            db.session.rollback()
            flash('An error occurred while updating the member.', category='error')

    return render_template(Config.TEMPLATES['edit_member'], member=member, user=current_user)

@auth.route('/delete_member/<int:member_id>', methods=['POST'])
@login_required
@admin_required
def delete_member(member_id):
    """Handle deleting a member."""
    member = Member.query.get_or_404(member_id)
    try:
        db.session.delete(member)
        db.session.commit()
        flash('Member deleted successfully!', category='success')
    except Exception:
        db.session.rollback()
        flash('An error occurred while deleting the member.', category='error')
    return redirect(url_for('auth.manage_members'))

@auth.route('/manage_events', methods=['GET'])
@login_required
@admin_required
def manage_events():
    """Handle event management with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    events = Event.query.order_by(Event.date).paginate(page=page, per_page=per_page)
    return render_template(Config.TEMPLATES['manage_events'], user=current_user, events=events)

@auth.route('/edit_event/<int:event_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_event(event_id):
    """Handle editing an event."""
    event = Event.query.get_or_404(event_id)

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        theme = request.form.get('theme', '').strip()
        involved = request.form.get('involved', '').strip()
        venue = request.form.get('venue', '').strip()
        date_str = request.form.get('date', '').strip()

        if not all([title, theme, involved, venue, date_str]):
            flash('All fields are required!', category='error')
            return render_template(Config.TEMPLATES['edit_event'], user=current_user, event=event)

        try:
            event.date = datetime.strptime(date_str, '%Y-%m-%d')
            event.title = title
            event.theme = theme
            event.involved = involved
            event.venue = venue
            db.session.commit()
            flash('Event updated successfully!', category='success')
            return redirect(url_for('auth.manage_events'))
        except ValueError:
            flash('Invalid date format. Use YYYY-MM-DD.', category='error')
        except Exception:
            db.session.rollback()
            flash('An error occurred while updating the event.', category='error')

    return render_template(Config.TEMPLATES['edit_event'], user=current_user, event=event)

@auth.route('/delete_event/<int:event_id>', methods=['POST'])
@login_required
@admin_required
def delete_event(event_id):
    """Handle deleting an event."""
    event = Event.query.get_or_404(event_id)
    try:
        db.session.delete(event)
        db.session.commit()
        flash('Event deleted successfully!', category='success')
    except Exception:
        db.session.rollback()
        flash('An error occurred while deleting the event.', category='error')
    return redirect(url_for('auth.manage_events'))

@auth.route('/member_dashboard', methods=['GET'])
@login_required
def member_dashboard():
    """Render member dashboard."""
    if current_user.__class__.__name__ == 'Admin':
        flash('Admins cannot access member dashboard.', category='error')
        return redirect(url_for('auth.admin_activities'))
    return render_template(Config.TEMPLATES['member_dashboard'])

@auth.route('/view_events', methods=['GET'])
@login_required
def view_events():
    """Display all events for members."""
    events = Event.query.order_by(Event.date).all()
    return render_template(Config.TEMPLATES['view_events'], events=events)

@auth.route('/view_readings', methods=['GET'])
@login_required
def view_readings():
    """Render readings page for members."""
    return render_template(Config.TEMPLATES['view_readings'])