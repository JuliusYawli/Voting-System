import os
from app import create_app, db
from app.models import Student, Admin, Election, Candidate, Vote, OTP

app = create_app(os.getenv('FLASK_ENV', 'default'))

@app.shell_context_processor
def make_shell_context():
    """Add database models to flask shell context."""
    return {
        'db': db,
        'Student': Student,
        'Admin': Admin,
        'Election': Election,
        'Candidate': Candidate,
        'Vote': Vote,
        'OTP': OTP
    }

if __name__ == '__main__':
    app.run(debug=True)
