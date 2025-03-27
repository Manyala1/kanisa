from flask import Blueprint, render_template, redirect, url_for, request, flash
from .models import Member
from . import db
from flask_login import login_user, logout_user, current_user, login_required  # Import login_required decorator
from werkzeug.security import generate_password_hash, check_password_hash  # Import for password hashing

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        zaq_number = request.form.get('zaq_number')
        phone_number = request.form.get('phone_number')

        member = Member.query.filter_by(zaq_number=zaq_number).first()

        if member and member.phone_number == phone_number:
            login_user(member, remember=True)
            flash('Login successful!', category='success')
            return redirect(url_for('views.home'))
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
    # Directly render the admin dashboard without requiring login
    return render_template('admin_dashboard.html')

@auth.route('/admin_login', methods=['GET', 'POST'], endpoint='admin_login')
def admin_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        admin = User.query.filter_by(email=email).first()
        if admin and check_password_hash(admin.password, password):
            login_user(admin, remember=True)
            flash('Admin login successful!', category='success')
            return redirect(url_for('auth.admin_dashboard'))
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
        confirm_password = request.form.get('confirm_password')  # Get the confirmation password

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match!', category='error')
            return redirect(url_for('auth.admin_signup'))

        # Check if the admin limit has been reached
        admin_count = User.query.count()
        if admin_count >= 2:
            flash('Admin limit reached. Only two admins are allowed.', category='error')
            return redirect(url_for('auth.admin_signup'))

        existing_admin = User.query.filter_by(email=email).first()
        if existing_admin:
            flash('Email already exists!', category='error')
        else:
            hashed_password = generate_password_hash(password, method='sha256')
            new_admin = User(
                full_name=full_name,
                email=email,
                phone_number=phone_number,
                password=hashed_password,
                jumuiya='',  # Optional fields can be left empty
                outstation='',
                center='',
                zone=''
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
