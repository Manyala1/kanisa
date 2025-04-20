@auth.route('/admin/activities')
def admin_activities():
    return render_template('admin_activities.html')
@auth.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # ...existing validation code...
        if valid_login:  # Replace with your actual validation logic
            flash('Login successful', 'success')
            return redirect(url_for('auth.admin_activities'))
    return render_template('admin_login.html')
