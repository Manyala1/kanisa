from flask import Blueprint, render_template, redirect, url_for, request, flash
from .models import Member, User, Admin, Event  # Import the new Event model
from . import db
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        zaq_number = request.form.get('zaq_number')
        phone_number = request.form.get('phone_number')

        member = Member.query.filter_by(zaq_number=zaq_number).first()

        if member and member.phone_number == phone_number:
            login_user(member, remember=True)  # Log in the member
            flash('Login successful!', category='success')
            return redirect(url_for('views.home'))  # Redirect to the events page
        else:
            flash('Invalid ZAQ Number or phone number.', category='error')

    return render_template('login.html', user=current_user)

@auth.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully!', category='info')
    return redirect(url_for('auth.login'))

@auth.route('/sign_up', methods=['GET', 'POST'], endpoint='sign_up')
def sign_up():
    if request.method == 'POST':
        full_name = request.form.get('full name')
        zaq_number = request.form.get('zaq_number')
        jumuiya = request.form.get('jumuiya')
        outstation = request.form.get('outstation')
        center = request.form.get('center')
        zone = request.form.get('zone')
        phone_number = request.form.get('phone_number')

        existing_member = Member.query.filter_by(zaq_number=zaq_number).first()
        if existing_member:
            flash('ZAQ Number already exists!', category='error')
        else:
            new_member = Member(
                zaq_number=zaq_number,
                full_name=full_name,
                phone_number=phone_number,
                jumuiya=jumuiya,
                outstation=outstation,
                center=center,
                zone=zone,
                user_id=current_user.id if current_user.is_authenticated else None
            )
            db.session.add(new_member)
            try:
                db.session.commit()
                flash('Signup successful! Please log in.', category='success')
                return redirect(url_for('auth.login'))
            except Exception as e:
                db.session.rollback()
                flash(f'An error occurred: {str(e)}', category='error')

    return render_template('sign_up.html', user=current_user)

@auth.route('/admin', endpoint='admin')
def admin_dashboard():
    return render_template('admin_dashboard.html')

@auth.route('/admin_login', methods=['GET', 'POST'], endpoint='admin_login')
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        admin = Admin.query.filter_by(email=email).first()
        if admin and check_password_hash(admin.password, password):
            login_user(admin, remember=True)
            flash('Admin login successful!', category='success')
            return redirect(url_for('auth.admin_activities'))
        else:
            flash('Invalid email or password.', category='error')

    return render_template('admin_login.html', user=current_user)

@auth.route('/admin_signup', methods=['GET', 'POST'], endpoint='admin_signup')
def admin_signup():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match!', category='error')
            return redirect(url_for('auth.admin_signup'))

        admin_count = Admin.query.count()
        if admin_count >= 2:
            flash('Admin limit reached. Only two admins are allowed.', category='error')
            return redirect(url_for('auth.admin_signup'))

        existing_admin = Admin.query.filter_by(email=email).first()
        if existing_admin:
            flash('Email already exists!', category='error')
        else:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_admin = Admin(
                full_name=full_name,
                email=email,
                phone_number=phone_number,
                password=hashed_password
            )
            db.session.add(new_admin)
            try:
                db.session.commit()
                flash('Admin account created successfully! Please log in.', category='success')
                return redirect(url_for('auth.admin_login'))
            except Exception as e:
                db.session.rollback()
                flash(f'An error occurred: {str(e)}', category='error')

    return render_template('admin_signup.html', user=current_user)

@auth.route('/admin_logout', methods=['GET'], endpoint='admin_logout')
def admin_logout():
    logout_user()
    flash('Admin logged out successfully!', category='info')
    return redirect(url_for('auth.admin_login'))

@auth.route('/admin_activities', endpoint='admin_activities')
def admin_activities():
    return render_template('admin_activities.html', user=current_user)

@auth.route('/add_event', methods=['GET', 'POST'], endpoint='add_event')
def add_event():
    if request.method == 'POST':
        title = request.form.get('title')
        theme = request.form.get('theme')  # New field for event theme
        involved = request.form.get('involved')  # New field for who is involved
        venue = request.form.get('venue')  # New field for venue
        date = request.form.get('date')

        # Create a new event with the additional fields
        new_event = Event(
            title=title,
            theme=theme,
            involved=involved,
            venue=venue,
            date=date,
            user_id=current_user.id
        )
        db.session.add(new_event)
        try:
            db.session.commit()
            flash('Event added successfully!', category='success')
            return redirect(url_for('auth.admin_activities'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', category='error')

    return render_template('add_event.html', user=current_user)

@auth.route('/add_member', methods=['GET', 'POST'], endpoint='add_member')
def add_member():
    if request.method == 'POST':
        full_name = request.form.get('full name')
        zaq_number = request.form.get('zaq_number')
        jumuiya = request.form.get('jumuiya')
        outstation = request.form.get('outstation')
        center = request.form.get('center')
        zone = request.form.get('zone')
        phone_number = request.form.get('phone_number')

        existing_member = Member.query.filter_by(zaq_number=zaq_number).first()
        if existing_member:
            flash('ZAQ Number already exists!', category='error')
        else:
            new_member = Member(
                zaq_number=zaq_number,
                full_name=full_name,
                phone_number=phone_number,
                jumuiya=jumuiya,
                outstation=outstation,
                center=center,
                zone=zone,
                user_id=None  # Admin is adding the member, so no user_id is linked
            )
            db.session.add(new_member)
            try:
                db.session.commit()
                flash('Member added successfully!', category='success')
                return redirect(url_for('auth.admin_activities'))
            except Exception as e:
                db.session.rollback()
                flash(f'An error occurred: {str(e)}', category='error')

    return render_template('sign_up.html', user=current_user)

@auth.route('/manage_members', methods=['GET', 'POST'], endpoint='manage_members')
def manage_members():
    search_query = request.args.get('search', '').strip()
    sort_by = request.args.get('sort_by', 'outstation')  # Default sort by outstation

    if search_query:
        # Search members by ZAQ number
        members = Member.query.filter(Member.zaq_number.like(f"%{search_query}%")).all()
    else:
        # Sort members by outstation or zone
        if sort_by == 'zone':
            members = Member.query.order_by(Member.zone).all()
        else:  # Default to sorting by outstation
            members = Member.query.order_by(Member.outstation).all()

    # Count members by outstation and zone
    outstation_counts = db.session.query(Member.outstation, db.func.count(Member.id)).group_by(Member.outstation).all()
    zone_counts = db.session.query(Member.zone, db.func.count(Member.id)).group_by(Member.zone).all()

    return render_template(
        'manage_members.html',
        user=current_user,
        members=members,
        outstation_counts=outstation_counts,
        zone_counts=zone_counts,
        search_query=search_query,
        sort_by=sort_by
    )

@auth.route('/edit_member/<int:member_id>', methods=['GET', 'POST'], endpoint='edit_member')
def edit_member(member_id):
    member = Member.query.get_or_404(member_id)

    if request.method == 'POST':
        member.full_name = request.form.get('full_name')
        member.zaq_number = request.form.get('zaq_number')
        member.jumuiya = request.form.get('jumuiya')
        member.outstation = request.form.get('outstation')
        member.center = request.form.get('center')
        member.zone = request.form.get('zone')
        member.phone_number = request.form.get('phone_number')

        try:
            db.session.commit()
            flash('Member updated successfully!', category='success')
            return redirect(url_for('auth.manage_members'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', category='error')

    return render_template('edit_member.html', member=member, user=current_user)

@auth.route('/delete_member/<int:member_id>', methods=['POST'], endpoint='delete_member')
def delete_member(member_id):
    member = Member.query.get_or_404(member_id)

    try:
        db.session.delete(member)
        db.session.commit()
        flash('Member deleted successfully!', category='success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', category='error')

    return redirect(url_for('auth.manage_members'))

@auth.route('/manage_events', methods=['GET'], endpoint='manage_events')
@login_required
def manage_events():
    events = Event.query.order_by(Event.date).all()
    return render_template('manage_events.html', user=current_user, events=events)

@auth.route('/edit_event/<int:event_id>', methods=['GET', 'POST'], endpoint='edit_event')
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)

    if request.method == 'POST':
        event.title = request.form.get('title')
        event.theme = request.form.get('theme')
        event.involved = request.form.get('involved')
        event.venue = request.form.get('venue')
        event.date = request.form.get('date')

        try:
            db.session.commit()
            flash('Event updated successfully!', category='success')
            return redirect(url_for('auth.manage_events'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', category='error')

    return render_template('edit_event.html', user=current_user, event=event)

@auth.route('/delete_event/<int:event_id>', methods=['POST'], endpoint='delete_event')
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)

    try:
        db.session.delete(event)
        db.session.commit()
        flash('Event deleted successfully!', category='success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', category='error')

    return redirect(url_for('auth.manage_events'))
