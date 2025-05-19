from datetime import datetime
from app import db
from app.models import Election, Candidate, Vote, Student

def get_active_elections():
    """Get all currently active elections."""
    now = datetime.utcnow()
    return Election.query.filter(
        Election.start_time <= now,
        Election.end_time >= now
    ).all()

def get_upcoming_elections():
    """Get all upcoming elections."""
    now = datetime.utcnow()
    return Election.query.filter(
        Election.start_time > now
    ).all()

def get_completed_elections():
    """Get all completed elections."""
    now = datetime.utcnow()
    return Election.query.filter(
        Election.end_time < now
    ).all()

def update_all_election_statuses():
    """Update the status of all elections based on current time."""
    elections = Election.query.all()
    for election in elections:
        election.check_status()
    return True

def can_student_vote(student_id, election_id):
    """Check if a student can vote in a specific election."""
    # Check if student exists
    student = Student.query.get(student_id)
    if not student:
        return False
    
    # Check if election exists and is active
    election = Election.query.get(election_id)
    if not election or not election.is_active:
        return False
    
    # Check if student has already voted in this election
    vote = Vote.query.filter_by(
        student_id=student_id,
        election_id=election_id
    ).first()
    
    return vote is None

def record_vote(student_id, candidate_id, election_id):
    """Record a vote from a student for a candidate in an election."""
    # Verify the student can vote
    if not can_student_vote(student_id, election_id):
        return False
    
    # Verify the candidate belongs to the election
    candidate = Candidate.query.get(candidate_id)
    if not candidate or candidate.election_id != election_id:
        return False
    
    # Create the vote record
    vote = Vote(
        student_id=student_id,
        candidate_id=candidate_id,
        election_id=election_id
    )
    
    # Update candidate vote count
    candidate.votes += 1
    
    # Mark student as having voted
    student = Student.query.get(student_id)
    student.has_voted = True
    
    # Commit to database
    db.session.add(vote)
    db.session.commit()
    
    return True

def get_election_results(election_id):
    """Get the results of an election."""
    election = Election.query.get(election_id)
    if not election:
        return None
    
    candidates = Candidate.query.filter_by(election_id=election_id).all()
    results = []
    
    total_votes = sum(c.votes for c in candidates)
    
    for candidate in candidates:
        percentage = 0
        if total_votes > 0:
            percentage = (candidate.votes / total_votes) * 100
            
        results.append({
            'id': candidate.id,
            'name': candidate.name,
            'votes': candidate.votes,
            'percentage': round(percentage, 2)
        })
    
    # Sort by votes (descending)
    results.sort(key=lambda x: x['votes'], reverse=True)
    
    return {
        'election': election,
        'candidates': results,
        'total_votes': total_votes
    }
