import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from datetime import datetime
from werkzeug.utils import secure_filename
from app import db
from app.models import Election, Candidate, Student, Vote
from app.forms.candidate_forms import CandidateForm
from app.utils.election import get_election_results

admin = Blueprint('admin', __name__)

@admin.before_request
def check_admin():
    """Ensure only authenticated admins can access admin routes."""
    if not current_user.is_authenticated:
        flash('Please log in as an admin to access this page.', 'danger')
        return redirect(url_for('auth.admin_login'))

@admin.route('/dashboard')
@login_required
def dashboard():
    """Admin dashboard showing overview of elections and system."""
    # Get counts for dashboard stats
    students_count = Student.query.count()
    elections_count = Election.query.count()
    candidates_count = Candidate.query.count()
    votes_count = Vote.query.count()
    
    # Get recent elections
    recent_elections = Election.query.order_by(Election.start_time.desc()).limit(5).all()
    
    # Get active elections
    now = datetime.utcnow()
    active_elections = Election.query.filter(
        Election.start_time <= now,
        Election.end_time >= now
    ).all()
    
    return render_template(
        'admin/dashboard.html',
        students_count=students_count,
        elections_count=elections_count,
        candidates_count=candidates_count,
        votes_count=votes_count,
        recent_elections=recent_elections,
        active_elections=active_elections
    )

@admin.route('/elections')
@login_required
def elections_list():
    """List all elections."""
    elections = Election.query.order_by(Election.start_time.desc()).all()
    return render_template('admin/elections_list.html', elections=elections)

@admin.route('/elections/new', methods=['GET', 'POST'])
@login_required
def election_create():
    """Create a new election."""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        start_time_str = request.form.get('start_time')
        end_time_str = request.form.get('end_time')
        
        if not title or not start_time_str or not end_time_str:
            flash('Title, start time, and end time are required.', 'danger')
            return render_template('admin/election_form.html')
        
        try:
            start_time = datetime.fromisoformat(start_time_str.replace('T', ' '))
            end_time = datetime.fromisoformat(end_time_str.replace('T', ' '))
        except ValueError:
            flash('Invalid date format.', 'danger')
            return render_template('admin/election_form.html')
        
        if start_time >= end_time:
            flash('End time must be after start time.', 'danger')
            return render_template('admin/election_form.html')
        
        election = Election(
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time
        )
        
        # Set initial status
        now = datetime.utcnow()
        if now < start_time:
            election.status = 'upcoming'
        elif now <= end_time:
            election.status = 'ongoing'
        else:
            election.status = 'completed'
        
        db.session.add(election)
        db.session.commit()
        
        flash('Election created successfully.', 'success')
        return redirect(url_for('admin.elections_list'))
    
    return render_template('admin/election_form.html')

@admin.route('/elections/<int:election_id>/edit', methods=['GET', 'POST'])
@login_required
def election_edit(election_id):
    """Edit an existing election."""
    election = Election.query.get_or_404(election_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        start_time_str = request.form.get('start_time')
        end_time_str = request.form.get('end_time')
        
        if not title or not start_time_str or not end_time_str:
            flash('Title, start time, and end time are required.', 'danger')
            return render_template('admin/election_form.html', election=election)
        
        try:
            start_time = datetime.fromisoformat(start_time_str.replace('T', ' '))
            end_time = datetime.fromisoformat(end_time_str.replace('T', ' '))
        except ValueError:
            flash('Invalid date format.', 'danger')
            return render_template('admin/election_form.html', election=election)
        
        if start_time >= end_time:
            flash('End time must be after start time.', 'danger')
            return render_template('admin/election_form.html', election=election)
        
        election.title = title
        election.description = description
        election.start_time = start_time
        election.end_time = end_time
        
        # Update status
        now = datetime.utcnow()
        if now < start_time:
            election.status = 'upcoming'
        elif now <= end_time:
            election.status = 'ongoing'
        else:
            election.status = 'completed'
        
        db.session.commit()
        
        flash('Election updated successfully.', 'success')
        return redirect(url_for('admin.elections_list'))
    
    # Format datetime for HTML datetime-local input
    election.start_time_str = election.start_time.strftime('%Y-%m-%dT%H:%M')
    election.end_time_str = election.end_time.strftime('%Y-%m-%dT%H:%M')
    
    return render_template('admin/election_form.html', election=election)

@admin.route('/elections/<int:election_id>/delete', methods=['POST'])
@login_required
def election_delete(election_id):
    """Delete an election."""
    election = Election.query.get_or_404(election_id)
    
    # Allow deletion of any election
    db.session.delete(election)
    db.session.commit()
    
    flash('Election deleted successfully.', 'success')
    return redirect(url_for('admin.elections_list'))

@admin.route('/elections/<int:election_id>/hide-results', methods=['POST'])
@login_required
def hide_election_results(election_id):
    """Hide the results of a completed election."""
    election = Election.query.get_or_404(election_id)
    
    if election.status != 'completed':
        flash('Can only hide results for completed elections.', 'danger')
        return redirect(url_for('admin.elections_list'))
    
    election.results_visible_until = None
    db.session.commit()
    
    flash('Election results have been hidden.', 'success')
    return redirect(url_for('admin.elections_list'))

@admin.route('/elections/<int:election_id>/candidates')
@login_required
def candidates_list(election_id):
    """List candidates for an election."""
    election = Election.query.get_or_404(election_id)
    candidates = Candidate.query.filter_by(election_id=election_id).all()
    
    return render_template(
        'admin/candidates_list.html',
        election=election,
        candidates=candidates
    )

@admin.route('/elections/<int:election_id>/candidates/new', methods=['GET', 'POST'])
@login_required
def candidate_create(election_id):
    """Create a new candidate for an election."""
    election = Election.query.get_or_404(election_id)
    form = CandidateForm()
    
    # Set the election_id to the current election
    form.election_id.data = election_id
    
    if form.validate_on_submit():
        # Handle file upload
        photo = form.photo.data
        if photo:
            # Generate a secure filename
            filename = Candidate.generate_filename(photo.filename)
            # Save the file
            photo_path = os.path.join(current_app.root_path, 'static', 'uploads', 'candidates', filename)
            photo.save(photo_path)
        else:
            filename = None
            
        # Create the candidate
        candidate = Candidate(
            name=form.name.data,
            election_id=election_id,
            bio=form.bio.data,
            photo=filename
        )
        
        db.session.add(candidate)
        db.session.commit()
        
        flash('Candidate added successfully.', 'success')
        return redirect(url_for('admin.candidates_list', election_id=election_id))
    
    return render_template('admin/candidate_form.html', form=form, election=election, title='Add Candidate')

@admin.route('/elections/<int:election_id>/candidates/<int:candidate_id>/edit', methods=['GET', 'POST'])
@login_required
def candidate_edit(election_id, candidate_id):
    """Edit an existing candidate."""
    election = Election.query.get_or_404(election_id)
    candidate = Candidate.query.get_or_404(candidate_id)
    
    if candidate.election_id != election_id:
        flash('Candidate does not belong to this election.', 'danger')
        return redirect(url_for('admin.candidates_list', election_id=election_id))
    
    form = CandidateForm(obj=candidate)
    # Set the election_id to the current election
    form.election_id.data = election_id
    
    if form.validate_on_submit():
        # Handle file upload if a new photo was provided
        if form.photo.data:
            # Delete old photo if it exists
            if candidate.photo:
                try:
                    os.remove(os.path.join(
                        current_app.root_path, 'static', 'uploads', 'candidates', candidate.photo
                    ))
                except OSError:
                    pass
            
            # Save new photo
            photo = form.photo.data
            filename = Candidate.generate_filename(photo.filename)
            photo_path = os.path.join(current_app.root_path, 'static', 'uploads', 'candidates', filename)
            photo.save(photo_path)
            candidate.photo = filename
        
        # Update other fields
        candidate.name = form.name.data
        candidate.bio = form.bio.data
        
        db.session.commit()
        
        flash('Candidate updated successfully.', 'success')
        return redirect(url_for('admin.candidates_list', election_id=election_id))
    
    return render_template('admin/candidate_form.html', form=form, election=election, candidate=candidate, title='Edit Candidate')

@admin.route('/elections/<int:election_id>/candidates/<int:candidate_id>/delete', methods=['POST'])
@login_required
def candidate_delete(election_id, candidate_id):
    """Delete a candidate and their photo."""
    election = Election.query.get_or_404(election_id)
    candidate = Candidate.query.get_or_404(candidate_id)
    
    if candidate.election_id != election_id:
        flash('Candidate does not belong to this election.', 'danger')
        return redirect(url_for('admin.candidates_list', election_id=election_id))
    
    # Delete the candidate's photo if it exists
    if candidate.photo:
        try:
            photo_path = os.path.join(
                current_app.root_path, 'static', 'uploads', 'candidates', candidate.photo
            )
            if os.path.exists(photo_path):
                os.remove(photo_path)
        except OSError as e:
            current_app.logger.error(f"Error deleting candidate photo: {e}")
    
    # Delete all votes for this candidate first
    Vote.query.filter_by(candidate_id=candidate_id).delete()
    
    # Now delete the candidate
    db.session.delete(candidate)
    db.session.commit()
    
    flash('Candidate deleted successfully.', 'success')
    return redirect(url_for('admin.candidates_list', election_id=election_id))

@admin.route('/elections/<int:election_id>/results')
@login_required
def election_results(election_id):
    """View results for an election."""
    results = get_election_results(election_id)
    
    if not results:
        flash('Election not found.', 'danger')
        return redirect(url_for('admin.elections_list'))
    
    return render_template('admin/election_results.html', results=results)

@admin.route('/elections/<int:election_id>/voters')
@login_required
def election_voters(election_id):
    """View list of students who have voted in an election."""
    election = Election.query.get_or_404(election_id)
    
    # Get students who have voted in this election
    voters = Student.query.join(Vote).filter(Vote.election_id == election_id).all()
    
    # Get total number of students
    total_students = Student.query.count()
    
    return render_template(
        'admin/election_voters.html',
        election=election,
        voters=voters,
        total_students=total_students,
        voters_count=len(voters)
    )
