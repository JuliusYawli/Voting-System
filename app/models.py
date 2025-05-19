from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager
import enum
import bcrypt

class UserType(enum.Enum):
    ADMIN = "admin"
    STUDENT = "student"

class Student(db.Model):
    """Student model representing university students who can vote."""
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    student_id = db.Column(db.String(20), nullable=False, unique=True)
    has_voted = db.Column(db.Boolean, default=False)
    
    # Relationships
    votes = db.relationship('Vote', backref='student', lazy='dynamic')
    
    def __repr__(self):
        return f'<Student {self.name}>'
    
    @property
    def masked_student_id(self):
        """Return a masked version of the student ID for verification."""
        if not self.student_id:
            return ""
        visible_chars = 3  # Number of characters to show at the end
        masked_length = len(self.student_id) - visible_chars
        return '*' * masked_length + self.student_id[-visible_chars:]

class Admin(UserMixin, db.Model):
    """Admin model representing system administrators."""
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    def __repr__(self):
        return f'<Admin {self.name}>'
    
    def set_password(self, password):
        """Set the password hash for the admin."""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    def check_password(self, password):
        """Check if the provided password matches the hash."""
        password_bytes = password.encode('utf-8')
        hash_bytes = self.password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    
    @property
    def user_type(self):
        return UserType.ADMIN

from datetime import datetime, timedelta

class Election(db.Model):
    """Election model representing voting events."""
    __tablename__ = 'elections'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='upcoming')  # upcoming, ongoing, completed
    results_visible_until = db.Column(db.DateTime, nullable=True)  # When None, results are not visible
    
    # Relationships
    candidates = db.relationship('Candidate', backref='election', lazy='dynamic', cascade='all, delete-orphan')
    votes = db.relationship('Vote', backref='election', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Election {self.title}>'
    
    @property
    def is_active(self):
        """Check if the election is currently active."""
        now = datetime.utcnow()
        return self.start_time <= now <= self.end_time
    
    @property
    def total_votes(self):
        """Get the total number of votes cast in this election."""
        return self.votes.count()
    
    def check_status(self):
        """Check and update the election status based on current time."""
        now = datetime.utcnow()
        old_status = self.status
        
        if now < self.start_time:
            self.status = 'upcoming'
        elif now <= self.end_time:
            self.status = 'ongoing'
        else:
            self.status = 'completed'
            # If the election just ended, set results to be visible for 1 week
            if old_status != 'completed':
                self.results_visible_until = now + timedelta(days=7)
        
        db.session.commit()

import os
import uuid
from datetime import datetime

class Candidate(db.Model):
    """Candidate model representing election candidates."""
    __tablename__ = 'candidates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    election_id = db.Column(db.Integer, db.ForeignKey('elections.id'), nullable=False)
    votes = db.Column(db.Integer, default=0)
    photo = db.Column(db.String(255), nullable=True)  # Path to the candidate's photo
    bio = db.Column(db.Text, nullable=True)  # Optional bio for the candidate
    
    # Relationships
    vote_records = db.relationship('Vote', backref='candidate', lazy='dynamic')
    
    def __repr__(self):
        return f'<Candidate {self.name}>'
    
    @staticmethod
    def generate_filename(original_filename):
        """Generate a unique filename for the uploaded photo."""
        ext = original_filename.rsplit('.', 1)[1].lower()
        return f"{uuid.uuid4()}.{ext}"
    
    @property
    def photo_url(self):
        """Return the URL to the candidate's photo or a default if none exists."""
        if self.photo:
            return url_for('static', filename=f'uploads/candidates/{self.photo}', _external=True)
        return url_for('static', filename='img/default-avatar.png', _external=True)

class Vote(db.Model):
    """Vote model representing individual votes cast by students."""
    __tablename__ = 'votes'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'), nullable=False)
    election_id = db.Column(db.Integer, db.ForeignKey('elections.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Vote {self.id}>'

class OTP(db.Model):
    """One-Time Password model for student authentication."""
    __tablename__ = 'otps'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    
    # Relationships
    student = db.relationship('Student', backref='otps')
    
    def __repr__(self):
        return f'<OTP {self.code}>'
    
    @property
    def is_expired(self):
        """Check if the OTP has expired."""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self):
        """Check if the OTP is still valid."""
        return not self.is_used and not self.is_expired

@login_manager.user_loader
def load_user(user_id):
    """Load a user for Flask-Login."""
    return Admin.query.get(int(user_id))
