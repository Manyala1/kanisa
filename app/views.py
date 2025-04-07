from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .models import Member, Event
from .api_utils import fetch_todays_readings  
from . import db
from datetime import datetime, timedelta

views = Blueprint('views', __name__)

@views.route('/', endpoint='landing')
def landing():
    # Render the landing page for unauthenticated users
    if current_user.is_authenticated:
        if current_user.__class__.__name__ == 'Admin':
            return redirect(url_for('auth.admin_activities'))
        return redirect(url_for('views.home'))
    return render_template('base.html')  # Show only the 3 routes for unauthenticated users

@views.route('/home', endpoint='home')
@login_required
def home():
    # Redirect admins to the admin activities page
    if current_user.__class__.__name__ == 'Admin':
        return redirect(url_for('auth.admin_activities'))
    # Render the home page for members
    return render_template('home.html', user=current_user)

@views.route('/add_member', methods=['GET', 'POST'])
@login_required
def add_member():
    # Ensure only admins can access this route
    if current_user.__class__.__name__ != 'Admin':
        flash('Access denied.', category='error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        zaq_number = request.form.get('zaq_number')
        full_name = request.form.get('full_name')
        phone_number = request.form.get('phone_number')
        jumuiya = request.form.get('jumuiya')
        outstation = request.form.get('outstation')
        center = request.form.get('center')
        zone = request.form.get('zone')

        if not zaq_number or not full_name or not phone_number:
            flash('All fields are required!', category='error')
        else:
            existing_member = Member.query.filter_by(zaq_number=zaq_number).first()
            if existing_member:
                flash('ZAQ number already exists!', category='error')
            else:
                new_member = Member(
                    zaq_number=zaq_number,
                    full_name=full_name,
                    phone_number=phone_number,
                    jumuiya=jumuiya,
                    outstation=outstation,
                    center=center,
                    zone=zone
                )
                db.session.add(new_member)
                db.session.commit()
                flash('Member added successfully!', category='success')
                return redirect(url_for('auth.manage_members'))

    return render_template('add_member.html', user=current_user)

@views.route('/add_event', methods=['GET', 'POST'])
@login_required
def add_event():
    # Ensure only admins can access this route
    if current_user.__class__.__name__ != 'Admin':
        flash('Access denied.', category='error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        title = request.form.get('title')
        date_str = request.form.get('date')
        venue = request.form.get('venue')
        theme = request.form.get('theme')
        involved = request.form.get('involved')

        if not title or not date_str or not venue or not theme or not involved:
            flash('All fields are required!', category='error')
        else:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d')
                new_event = Event(
                    title=title,
                    date=date,
                    venue=venue,
                    theme=theme,
                    involved=involved
                )
                db.session.add(new_event)
                db.session.commit()
                flash('Event added successfully!', category='success')
                return redirect(url_for('auth.manage_events'))
            except ValueError:
                flash('Invalid date format! Use YYYY-MM-DD', category='error')

    return render_template('add_event.html', user=current_user)

@views.route('/view_events', methods=['GET'], endpoint='view_events')
@login_required
def view_events():
    # Fetch all events from the database
    events = Event.query.order_by(Event.date).all()
    return render_template('view_events.html', user=current_user, events=events)

@views.route('/view_readings', methods=['GET'], endpoint='view_readings')
@login_required
def view_readings():
    # Fetch today's readings using the updated API utility
    readings = fetch_todays_readings()
    if not readings:
        flash("No daily readings available today. Please check back later.", category="info")
        return render_template('view_readings.html', user=current_user, readings={})
    return render_template('view_readings.html', user=current_user, readings=readings)