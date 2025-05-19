from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, IntegerField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Optional
from app.models import Election

class CandidateForm(FlaskForm):
    """Form for adding or editing a candidate."""
    name = StringField('Full Name', validators=[DataRequired(), Length(max=100)])
    election_id = SelectField('Election', coerce=int, validators=[DataRequired()])
    bio = TextAreaField('Biography', validators=[Optional(), Length(max=500)])
    photo = FileField('Profile Photo', validators=[
        FileRequired(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Only image files (jpg, jpeg, png) are allowed.')
    ])
    submit = SubmitField('Save Candidate')

    def __init__(self, *args, **kwargs):
        super(CandidateForm, self).__init__(*args, **kwargs)
        # Populate the election dropdown with active elections
        self.election_id.choices = [(e.id, e.title) for e in 
                                  Election.query.order_by(Election.title).all()]
