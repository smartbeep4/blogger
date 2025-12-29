from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, HiddenField
from wtforms.validators import DataRequired, Length, ValidationError
from app.models import User


class LoginForm(FlaskForm):
    """Login form for user authentication."""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class UserForm(FlaskForm):
    """Form for creating/editing users (admin only)."""
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    role = SelectField('Role', choices=[('author', 'Author'), ('admin', 'Admin')],
                      validators=[DataRequired()])
    submit = SubmitField('Save User')

    def validate_username(self, username):
        """Check if username is already taken."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists.')


class PostForm(FlaskForm):
    """Form for post creation/editing."""
    title = StringField('Title', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    status = SelectField('Status', choices=[('draft', 'Draft'), ('published', 'Published')])
    submit = SubmitField('Save Post')


class QuizForm(FlaskForm):
    """Form for quiz creation."""
    question_text = TextAreaField('Question', validators=[DataRequired()])
    question_type = SelectField('Type', choices=[
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False')
    ], validators=[DataRequired()])
    options = TextAreaField('Options (one per line)', validators=[DataRequired()])
    correct_answer = StringField('Correct Answer', validators=[DataRequired()])
    submit = SubmitField('Add Question')


class ChartForm(FlaskForm):
    """Form for chart creation."""
    chart_type = SelectField('Chart Type', choices=[
        ('bar', 'Bar Chart'),
        ('line', 'Line Chart'),
        ('pie', 'Pie Chart'),
        ('doughnut', 'Doughnut Chart')
    ], validators=[DataRequired()])
    data = TextAreaField('Data (JSON format)', validators=[DataRequired()])
    submit = SubmitField('Create Chart')


class VideoForm(FlaskForm):
    """Form for video upload/URL."""
    url = StringField('Video URL', validators=[DataRequired()])
    submit = SubmitField('Add Video')


class PDFForm(FlaskForm):
    """Form for PDF upload."""
    pdf_file = HiddenField('PDF File')  # Will be handled by JavaScript
    submit = SubmitField('Upload PDF')
