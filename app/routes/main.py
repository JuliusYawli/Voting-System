from flask import Blueprint, render_template, current_app
from app.models import Election, Candidate
from app.utils.election import get_active_elections, get_completed_elections, update_all_election_statuses
from datetime import datetime

main = Blueprint('main', __name__)

@main.context_processor
def inject_current_year():
    """Inject the current year into all templates."""
    return {'current_year': datetime.now().year}

@main.before_app_request
def update_election_statuses():
    """Update all election statuses before handling requests."""
    update_all_election_statuses()

@main.route('/')
def index():
    """Landing page showing upcoming elections only."""
    now = datetime.utcnow()
    
    # Get only upcoming elections
    upcoming_elections = Election.query.filter(
        Election.start_time > now
    ).order_by(Election.start_time.asc()).all()
    
    # Update status of all elections
    for election in upcoming_elections:
        election.check_status()
    
    return render_template('index.html', 
                          elections=upcoming_elections,
                          election_data=[])  # No charts on landing page
    
    return render_template(
        'index.html',
        active_elections=active_elections,
        completed_elections=completed_elections,
        election_data=election_data
    )

@main.route('/about')
def about():
    """About page with information about the e-voting system."""
    return render_template('about.html')

@main.route('/contact')
def contact():
    """Contact page with contact information."""
    return render_template('contact.html')

@main.route('/election/<int:election_id>')
def election_details(election_id):
    """Public page showing details of a specific election."""
    election = Election.query.get_or_404(election_id)
    candidates = Candidate.query.filter_by(election_id=election_id).all()
    
    # Calculate total votes and percentages
    total_votes = sum(candidate.votes for candidate in candidates)
    
    candidate_data = []
    for candidate in candidates:
        percentage = 0
        if total_votes > 0:
            percentage = (candidate.votes / total_votes) * 100
            
        candidate_data.append({
            'id': candidate.id,
            'name': candidate.name,
            'votes': candidate.votes,
            'percentage': round(percentage, 2)
        })
    
    return render_template(
        'election_details.html',
        election=election,
        candidates=candidate_data,
        total_votes=total_votes
    )
