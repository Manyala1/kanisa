from flask import Blueprint, render_template, redirect, url_for, request, flash
from .models import Member
from . import db
from flask_login import login_user, logout_user, current_user

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
    return render_template('admin_dashboard.html', user=current_user)
