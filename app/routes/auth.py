from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import Student, Admin
from app.utils.email import create_otp_for_student, send_otp_email, verify_otp
from werkzeug.security import check_password_hash

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    """Login page for both students and admins."""
    if request.method == 'POST':
        email = request.form.get('email')
        user_type = request.form.get('user_type')
        
        if not email or not user_type:
            flash('Email and user type are required.', 'danger')
            return redirect(url_for('auth.login'))
        
        if user_type == 'student':
            return redirect(url_for('auth.student_verify', email=email))
        elif user_type == 'admin':
            return redirect(url_for('auth.admin_login'))
        else:
            flash('Invalid user type.', 'danger')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/login.html')

@auth.route('/student/verify', methods=['GET', 'POST'])
def student_verify():
    """Verify student identity by showing masked student ID."""
    email = request.args.get('email')
    
    if not email:
        flash('Email is required.', 'danger')
        return redirect(url_for('auth.login'))
    
    student = Student.query.filter_by(email=email).first()
    
    if not student:
        flash('No student found with that email.', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        
        if not student_id:
            flash('Student ID is required.', 'danger')
            return render_template('auth/student_verify.html', email=email, masked_id=student.masked_student_id)
        
        if student_id != student.student_id:
            flash('Incorrect student ID.', 'danger')
            return render_template('auth/student_verify.html', email=email, masked_id=student.masked_student_id)
        
        # Generate and send OTP
        otp = create_otp_for_student(student)
        send_otp_email(student, otp)
        
        # Store student ID in session for OTP verification
        session['verifying_student_id'] = student.id
        
        # For testing: Display OTP in browser
        flash(f'For testing purposes only: Your OTP is {otp.code}', 'warning')
        
        flash('In a production environment, the OTP would be sent to your email.', 'info')
        return redirect(url_for('auth.student_otp'))
    
    return render_template('auth/student_verify.html', email=email, masked_id=student.masked_student_id)

@auth.route('/student/otp', methods=['GET', 'POST'])
def student_otp():
    """Verify student OTP."""
    student_id = session.get('verifying_student_id')
    
    if not student_id:
        flash('Session expired. Please start again.', 'danger')
        return redirect(url_for('auth.login'))
    
    student = Student.query.get(student_id)
    
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        otp_code = request.form.get('otp')
        
        if not otp_code:
            flash('OTP is required.', 'danger')
            return render_template('auth/student_otp.html')
        
        if verify_otp(student_id, otp_code):
            # Store authenticated student in session
            session['student_id'] = student_id
            session['student_name'] = student.name
            
            # Clear verification session
            session.pop('verifying_student_id', None)
            
            flash('Login successful!', 'success')
            flash(f'Welcome, {student.name}!', 'success')
            return redirect(url_for('voter.dashboard'))
        else:
            flash('Invalid OTP. Please try again.', 'danger')
            return render_template('auth/student_otp.html')
    
    return render_template('auth/student_otp.html')

@auth.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email and password are required.', 'danger')
            return render_template('auth/admin_login.html')
        
        admin = Admin.query.filter_by(email=email).first()
        
        if not admin or not admin.check_password(password):
            flash('Invalid email or password.', 'danger')
            return render_template('auth/admin_login.html')
        
        login_user(admin)
        
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('admin.dashboard')
            
        flash(f'Welcome, {admin.name}!', 'success')
        return redirect(next_page)
    
    return render_template('auth/admin_login.html')

@auth.route('/logout')
def logout():
    """Logout route for both students and admins."""
    if current_user.is_authenticated:
        logout_user()
        flash('You have been logged out.', 'info')
    else:
        # For student session-based auth
        session.pop('student_id', None)
        session.pop('student_name', None)
        flash('You have been logged out.', 'info')
    
    return redirect(url_for('main.index'))
