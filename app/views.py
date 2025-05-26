from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from .models import Member, Event
from .api_utils import fetch_todays_readings  
from . import db
from datetime import datetime, timedelta
import logging


views = Blueprint('views', __name__)

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
    if current_user.__class__.__name__ != 'Admin':
        flash('Access denied.', category='error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        zaq_number = request.form.get('zaq_number')
        full_name = request.form.get('full_name')
        phone_number = request.form.get('phone_number')
        email = request.form.get('email')
        jumuiya = request.form.get('jumuiya')
        outstation = request.form.get('outstation')
        center = request.form.get('center')
        zone = request.form.get('zone')

        # Validate required fields
        if not all([zaq_number, full_name, phone_number, email]):
            flash('All fields marked with * are required!', category='error')
            return render_template('add_member.html', user=current_user)

        # Validate phone number format
        if not phone_number.isdigit() or len(phone_number) != 10:
            flash('Phone number must be exactly 10 digits!', category='error')
            return render_template('add_member.html', user=current_user)

        # Validate email format
        if '@' not in email:
            flash('Please enter a valid email address!', category='error')
            return render_template('add_member.html', user=current_user)

        # Check for existing member with same ZAQ, phone, or email
        if Member.query.filter_by(zaq_number=zaq_number).first():
            flash('ZAQ number already exists!', category='error')
        elif Member.query.filter_by(phone_number=phone_number).first():
            flash('Phone number already registered!', category='error')
        elif Member.query.filter_by(email=email).first():
            flash('Email already registered!', category='error')
        else:
            try:
                new_member = Member(
                    zaq_number=zaq_number,
                    full_name=full_name,
                    phone_number=phone_number,
                    email=email,
                    jumuiya=jumuiya,
                    outstation=outstation,
                    center=center,
                    zone=zone
                )
                db.session.add(new_member)
                db.session.commit()
                flash('Member added successfully!', category='success')
                return redirect(url_for('auth.admin_activities'))
            except Exception as e:
                db.session.rollback()
                flash('Error adding member. Please try again.', category='error')
                current_app.logger.error(f"Error adding member: {str(e)}")

    return render_template('add_member.html', user=current_user)

@views.route('/add_event', methods=['GET', 'POST'])
@login_required
def add_event():
    # Ensure only admins can access this route
    if not current_user.is_admin:
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
                # Convert string date to datetime object
                event_date = datetime.strptime(date_str, '%Y-%m-%d')
                
                # Get today's date with time set to midnight for comparison
                today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                
                # Check if event date is before today
                if event_date < today:
                    flash('Event date cannot be in the past!', category='error')
                    return render_template('add_event.html', user=current_user)

                new_event = Event(
                    title=title,
                    date=event_date,
                    venue=venue,
                    theme=theme,
                    involved=involved,
                    admin_id=current_user.id
                )
                db.session.add(new_event)
                db.session.commit()
                flash('Event added successfully!', category='success')
                return redirect(url_for('auth.manage_events'))
            except ValueError:
                flash('Invalid date format! Use YYYY-MM-DD', category='error')
            except Exception as e:
                db.session.rollback()
                flash(f'Error adding event: {str(e)}', category='error')

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
    try:
        current_app.logger.debug("Attempting to fetch readings...")
        readings = fetch_todays_readings()
        
        if not readings:
            current_app.logger.error("No readings data received from USCCB")
            flash('Unable to fetch today\'s readings. Please try again later.', 'error')
            return redirect(url_for('views.home'))
        
        # Log the received data for debugging
        current_app.logger.debug(f"Received readings data: {readings}")
        
        # Validate the data structure
        required_keys = ['date', 'liturgical_info', 'readings']
        if not all(key in readings for key in required_keys):
            raise ValueError("Invalid readings data structure")
            
        # Enhance liturgical information
        liturgical_info = readings.get('liturgical_info', {})
        calendar_info = {
            'season': liturgical_info.get('season', 'Ordinary Time'),
            'celebration': liturgical_info.get('celebration', ''),
            'is_feast': 'feast' in (liturgical_info.get('celebration', '').lower()),
            'is_solemnity': 'solemnity' in (liturgical_info.get('celebration', '').lower()),
            'date': readings.get('date', datetime.now().strftime('%Y-%m-%d'))
        }
        
        return render_template('view_readings.html', 
                             readings=readings,
                             calendar_info=calendar_info,
                             error=None)
        
    except Exception as e:
        current_app.logger.error(f"Error in view_readings: {str(e)}")
        return render_template('view_readings.html', 
                             readings=None,
                             error="Unable to fetch today's readings. Please try again later.")

@views.route('/about', methods=['GET'], endpoint='about')
def about():
    return render_template('about.html')

@views.route('/', endpoint='landing')
def landing():
    return render_template('base.html')