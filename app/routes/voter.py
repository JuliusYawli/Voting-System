from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required
from app import db
from app.models import Student, Election, Candidate, Vote
from app.utils.election import get_active_elections, can_student_vote, record_vote
from datetime import datetime

voter = Blueprint('voter', __name__)

@voter.before_request
def check_student():
    """Ensure only authenticated students can access voter routes."""
    if 'student_id' not in session:
        flash('Please log in to access this page.', 'danger')
        return redirect(url_for('auth.login'))

@voter.route('/dashboard')
def dashboard():
    """Student dashboard showing available and completed elections."""
    student_id = session.get('student_id')
    if not student_id:
        flash('Please log in to access your dashboard.', 'warning')
        return redirect(url_for('auth.login'))
    
    student = Student.query.get(student_id)
    if not student:
        flash('Student account not found.', 'danger')
        session.clear()
        return redirect(url_for('auth.login'))
    
    now = datetime.utcnow()
    
    # Get active elections
    active_elections = Election.query.filter(
        Election.start_time <= now,
        Election.end_time >= now
    ).order_by(Election.end_time.asc()).all()
    
    # Get completed elections with visible results
    completed_elections = Election.query.filter(
        Election.end_time < now,
        Election.status == 'completed',
        Election.results_visible_until > now
    ).order_by(Election.end_time.desc()).all()
    
    # Get student's voting history
    student_votes = Vote.query.filter_by(student_id=student_id).all()
    voted_election_ids = [vote.election_id for vote in student_votes]
    
    # Get results for completed elections
    election_results = []
    for election in completed_elections:
        candidates = Candidate.query.filter_by(election_id=election.id).all()
        total_votes = sum(c.votes for c in candidates)
        
        # Sort candidates by votes in descending order
        candidates = sorted(candidates, key=lambda c: c.votes, reverse=True)
        
        election_results.append({
            'election': election,
            'winner': candidates[0] if candidates else None,
            'candidates': candidates,
            'total_votes': total_votes
        })
    
    return render_template(
        'voter/dashboard.html',
        student=student,
        active_elections=active_elections,
        voted_election_ids=voted_election_ids,
        election_results=election_results
    )

@voter.route('/election/<int:election_id>')
def election_details(election_id):
    """View details of an election and vote if eligible."""
    student_id = session.get('student_id')
    student = Student.query.get(student_id)
    
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('auth.login'))
    
    election = Election.query.get_or_404(election_id)
    
    # Check if election is active
    now = datetime.utcnow()
    if not (election.start_time <= now <= election.end_time):
        flash('This election is not currently active.', 'warning')
        return redirect(url_for('voter.dashboard'))
    
    # Check if student has already voted
    vote = Vote.query.filter_by(
        student_id=student_id,
        election_id=election_id
    ).first()
    
    if vote:
        flash('You have already voted in this election.', 'info')
        return redirect(url_for('voter.view_receipt', election_id=election_id))
    
    # Get candidates
    candidates = Candidate.query.filter_by(election_id=election_id).all()
    
    if not candidates:
        flash('No candidates available for this election.', 'warning')
        return redirect(url_for('voter.dashboard'))
    
    return render_template(
        'voter/election_details.html',
        election=election,
        candidates=candidates
    )

@voter.route('/election/<int:election_id>/vote', methods=['POST'])
def vote(election_id):
    """Process a vote for an election."""
    student_id = session.get('student_id')
    student = Student.query.get(student_id)
    
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('auth.login'))
    
    candidate_id = request.form.get('candidate_id')
    
    if not candidate_id:
        flash('Please select a candidate.', 'danger')
        return redirect(url_for('voter.election_details', election_id=election_id))
    
    # Check if student can vote
    if not can_student_vote(student_id, election_id):
        flash('You are not eligible to vote in this election.', 'danger')
        return redirect(url_for('voter.dashboard'))
    
    # Record the vote
    success = record_vote(student_id, int(candidate_id), election_id)
    
    if success:
        flash('Your vote has been recorded successfully.', 'success')
        return redirect(url_for('voter.view_receipt', election_id=election_id))
    else:
        flash('Failed to record your vote. Please try again.', 'danger')
        return redirect(url_for('voter.election_details', election_id=election_id))

@voter.route('/election/<int:election_id>/receipt')
def view_receipt(election_id):
    """View receipt of a vote."""
    student_id = session.get('student_id')
    student = Student.query.get(student_id)
    
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('auth.login'))
    
    election = Election.query.get_or_404(election_id)
    
    # Check if student has voted
    vote = Vote.query.filter_by(
        student_id=student_id,
        election_id=election_id
    ).first()
    
    if not vote:
        flash('You have not voted in this election.', 'warning')
        return redirect(url_for('voter.dashboard'))
    
    # Get the candidate voted for
    candidate = Candidate.query.get(vote.candidate_id)
    
    return render_template(
        'voter/receipt.html',
        election=election,
        vote=vote,
        candidate=candidate
    )

@voter.route('/history')
def voting_history():
    """View voting history for the student."""
    student_id = session.get('student_id')
    student = Student.query.get(student_id)
    
    if not student:
        flash('Student not found.', 'danger')
        return redirect(url_for('auth.login'))
    
    # Get all votes by this student
    votes = Vote.query.filter_by(student_id=student_id).all()
    
    vote_history = []
    for vote in votes:
        election = Election.query.get(vote.election_id)
        candidate = Candidate.query.get(vote.candidate_id)
        
        vote_history.append({
            'election': election,
            'candidate': candidate,
            'timestamp': vote.timestamp
        })
    
    return render_template(
        'voter/history.html',
        student=student,
        vote_history=vote_history
    )
