import random
import string
from datetime import datetime, timedelta
from flask import current_app, render_template
from flask_mail import Message
from app import mail, db
from app.models import OTP

def generate_otp(length=6):
    """Generate a random OTP code of specified length."""
    return ''.join(random.choices(string.digits, k=length))

def create_otp_for_student(student):
    """Create and save a new OTP for a student."""
    # Invalidate any existing OTPs for this student
    existing_otps = OTP.query.filter_by(student_id=student.id, is_used=False).all()
    for otp in existing_otps:
        otp.is_used = True
    
    # Create new OTP
    code = generate_otp()
    expiry_seconds = current_app.config.get('OTP_EXPIRY_SECONDS', 300)  # Default 5 minutes
    expires_at = datetime.utcnow() + timedelta(seconds=expiry_seconds)
    
    new_otp = OTP(
        student_id=student.id,
        code=code,
        expires_at=expires_at
    )
    
    db.session.add(new_otp)
    db.session.commit()
    
    return new_otp

def send_otp_email(student, otp):
    """Send OTP to student's email."""
    subject = "RMU E-Voting System - Your OTP Code"
    
    # For development, just print to console
    if current_app.debug:
        print(f"\n")
        print(f"*" * 50)
        print(f"***** OTP EMAIL *****")
        print(f"*" * 50)
        print(f"To: {student.email}")
        print(f"Subject: {subject}")
        print(f"")
        print(f"OTP CODE: {otp.code}")
        print(f"")
        print(f"Valid until: {otp.expires_at}")
        print(f"*" * 50)
        print(f"\n")
        # Also log to the application logger
        current_app.logger.info(f"OTP for {student.email}: {otp.code}")
        return True
    
    # For production, send actual email
    try:
        msg = Message(
            subject=subject,
            recipients=[student.email]
        )
        msg.body = f"""
Hello {student.name},

Your One-Time Password (OTP) for the RMU E-Voting System is: {otp.code}

This code will expire in 5 minutes.

Please do not share this code with anyone.

Regards,
RMU E-Voting System
        """
        
        msg.html = f"""
<p>Hello {student.name},</p>

<p>Your One-Time Password (OTP) for the RMU E-Voting System is: <strong>{otp.code}</strong></p>

<p>This code will expire in 5 minutes.</p>

<p>Please do not share this code with anyone.</p>

<p>Regards,<br>
RMU E-Voting System</p>
        """
        
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {str(e)}")
        return False

def verify_otp(student_id, code):
    """Verify if the provided OTP is valid for the student."""
    otp = OTP.query.filter_by(
        student_id=student_id,
        code=code,
        is_used=False
    ).first()
    
    if not otp:
        return False
    
    if otp.is_expired:
        return False
    
    # Mark OTP as used
    otp.is_used = True
    db.session.commit()
    
    return True
