from flask import Blueprint, render_template, redirect, url_for, flash, request, session, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_limiter import Limiter
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from bleach import clean
from datetime import datetime, timedelta
import re
import os

from app import db, limiter
from app.models import User, Post, BlockedIP, AnalyticsLog, Quiz, Chart, Video, Revision
from app.forms import LoginForm, UserForm, PostForm, QuizForm, ChartForm, VideoForm, PDFForm
from app.utils import sanitize_input, parse_shortcodes, generate_tags_with_ai, allowed_file

bp = Blueprint('main', __name__)


# Authentication Routes
@bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per 5 minutes")
def login():
    """Handle user login with rate limiting and IP blocking."""
    # Check if IP is blocked
    blocked_ip = BlockedIP.query.filter_by(ip_address=request.remote_addr).first()
    if blocked_ip:
        flash('Your IP address has been blocked due to multiple failed login attempts.', 'danger')
        return render_template('login.html', form=LoginForm())

    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        # Sanitize username input
        username = clean(form.username.data.strip(), tags=[], strip=True)
        password = form.password.data

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            # Successful login
            login_user(user, remember=form.remember_me.data)
            user.failed_attempts = 0
            db.session.commit()

            # Log successful login
            log_entry = AnalyticsLog(
                post_id=0,  # No specific post for login
                event_type='login_success',
                ip_address=request.remote_addr
            )
            db.session.add(log_entry)
            db.session.commit()

            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.dashboard')
            return redirect(next_page)
        else:
            # Failed login
            if user:
                user.failed_attempts += 1
                user.last_attempt = datetime.utcnow()

                # Block IP if too many attempts
                if user.failed_attempts >= 5:
                    blocked = BlockedIP(
                        ip_address=request.remote_addr,
                        reason=f'Multiple failed login attempts for user {username}'
                    )
                    db.session.add(blocked)
                    flash('Account locked due to multiple failed attempts. Contact admin.', 'danger')
                else:
                    flash('Invalid username or password.', 'danger')
                db.session.commit()
            else:
                flash('Invalid username or password.', 'danger')

            # Log failed login attempt
            log_entry = AnalyticsLog(
                post_id=0,
                event_type='login_failed',
                ip_address=request.remote_addr
            )
            db.session.add(log_entry)
            db.session.commit()

    return render_template('login.html', form=form)


@bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    return redirect(url_for('main.index'))


# Public Routes
@bp.route('/')
def index():
    """Blog index with published posts."""
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(status='published')\
                     .order_by(Post.published_at.desc())\
                     .paginate(page=page, per_page=10, error_out=False)

    return render_template('index.html', posts=posts)


@bp.route('/post/<slug>')
def post(slug):
    """Single post view."""
    post = Post.query.filter_by(slug=slug, status='published').first_or_404()

    # Increment view count
    post.increment_views()

    # Log view analytics
    log_entry = AnalyticsLog(
        post_id=post.id,
        event_type='view',
        ip_address=request.remote_addr
    )
    db.session.add(log_entry)
    db.session.commit()

    # Parse shortcodes in content
    parsed_content = parse_shortcodes(post.content)

    return render_template('post.html', post=post, content=parsed_content)


@bp.route('/category/<category>')
def category(category):
    """Posts by category."""
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter(
        Post.status == 'published',
        Post.categories.contains([category])
    ).order_by(Post.published_at.desc())\
     .paginate(page=page, per_page=10, error_out=False)

    return render_template('index.html', posts=posts, category=category)


@bp.route('/tag/<tag>')
def tag(tag):
    """Posts by tag."""
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter(
        Post.status == 'published',
        Post.tags.contains([tag])
    ).order_by(Post.published_at.desc())\
     .paginate(page=page, per_page=10, error_out=False)

    return render_template('index.html', posts=posts, tag=tag)


# Protected Routes
@bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard with analytics."""
    posts = Post.query.filter_by(author_id=current_user.id)\
                     .order_by(Post.updated_at.desc())\
                     .all()

    # Aggregate analytics data
    total_views = sum(post.views for post in posts)
    total_posts = len(posts)
    published_posts = len([p for p in posts if p.status == 'published'])

    return render_template('dashboard.html',
                         posts=posts,
                         total_views=total_views,
                         total_posts=total_posts,
                         published_posts=published_posts)


@bp.route('/editor', methods=['GET', 'POST'])
@login_required
def editor():
    """Main editor interface."""
    post_id = request.args.get('post_id', type=int)
    post = None

    if post_id:
        post = Post.query.filter_by(id=post_id, author_id=current_user.id).first_or_404()

    form = PostForm(obj=post) if post else PostForm()

    if form.validate_on_submit():
        if post:
            # Update existing post
            post.title = sanitize_input(form.title.data, ['b', 'i', 'u', 'strong', 'em'])
            post.content = form.content.data  # Will be sanitized before saving
            post.status = form.status.data
            post.updated_at = datetime.utcnow()
        else:
            # Create new post
            post = Post(
                title=sanitize_input(form.title.data, ['b', 'i', 'u', 'strong', 'em']),
                content=form.content.data,
                status=form.status.data,
                author_id=current_user.id
            )
            post.generate_slug()
            db.session.add(post)

        db.session.commit()

        if form.status.data == 'published' and not post.published_at:
            post.published_at = datetime.utcnow()
            # Generate AI tags and categories
            try:
                ai_tags = generate_tags_with_ai(post.content)
                post.categories = ai_tags.get('categories', [])
                post.tags = ai_tags.get('tags', [])
            except Exception as e:
                print(f"AI tag generation failed: {e}")

            # Create revision for version history
            revision = Revision(post_id=post.id, content=post.content)
            db.session.add(revision)

        db.session.commit()
        flash('Post saved successfully!', 'success')
        return redirect(url_for('main.editor', post_id=post.id))

    return render_template('editor.html', form=form, post=post)


# API Routes for AJAX interactions
@bp.route('/api/save_draft', methods=['POST'])
@login_required
def save_draft():
    """Auto-save draft via AJAX."""
    data = request.get_json()
    post_id = data.get('post_id')
    content = data.get('content', '')

    if post_id:
        post = Post.query.filter_by(id=post_id, author_id=current_user.id).first()
        if post:
            post.content = content
            post.updated_at = datetime.utcnow()
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Draft saved'})
    else:
        # Create new draft
        post = Post(
            title='Untitled Draft',
            content=content,
            status='draft',
            author_id=current_user.id
        )
        db.session.add(post)
        db.session.commit()
        return jsonify({'status': 'success', 'post_id': post.id, 'message': 'Draft created'})

    return jsonify({'status': 'error', 'message': 'Failed to save draft'}), 400


@bp.route('/api/publish', methods=['POST'])
@login_required
def publish():
    """Publish post via AJAX."""
    data = request.get_json()
    post_id = data.get('post_id')

    post = Post.query.filter_by(id=post_id, author_id=current_user.id).first()
    if not post:
        return jsonify({'status': 'error', 'message': 'Post not found'}), 404

    post.status = 'published'
    if not post.published_at:
        post.published_at = datetime.utcnow()

        # Generate AI tags and categories
        try:
            ai_tags = generate_tags_with_ai(post.content)
            post.categories = ai_tags.get('categories', [])
            post.tags = ai_tags.get('tags', [])
        except Exception as e:
            print(f"AI tag generation failed: {e}")

    # Create revision for version history
    revision = Revision(post_id=post.id, content=post.content)
    db.session.add(revision)
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Post published'})


@bp.route('/api/create_quiz', methods=['POST'])
@login_required
def create_quiz():
    """Create quiz via AJAX."""
    data = request.get_json()
    post_id = data.get('post_id')
    questions = data.get('questions', [])

    if not post_id or not questions:
        return jsonify({'status': 'error', 'message': 'Missing data'}), 400

    quiz = Quiz(post_id=post_id, questions=questions)
    db.session.add(quiz)
    db.session.commit()

    return jsonify({'status': 'success', 'quiz_id': quiz.id, 'shortcode': f'[quiz id={quiz.id}]'})


@bp.route('/api/create_chart', methods=['POST'])
@login_required
def create_chart():
    """Create chart via AJAX."""
    data = request.get_json()
    post_id = data.get('post_id')
    chart_type = data.get('chart_type')
    chart_data = data.get('data', {})

    if not post_id or not chart_type or not chart_data:
        return jsonify({'status': 'error', 'message': 'Missing data'}), 400

    chart = Chart(post_id=post_id, chart_type=chart_type, data=chart_data)
    db.session.add(chart)
    db.session.commit()

    return jsonify({'status': 'success', 'chart_id': chart.id, 'shortcode': f'[chart id={chart.id}]'})


@bp.route('/api/upload_video', methods=['POST'])
@login_required
def upload_video():
    """Handle video upload."""
    if 'video' not in request.files:
        return jsonify({'status': 'error', 'message': 'No video file'}), 400

    file = request.files['video']
    post_id = request.form.get('post_id')

    if not post_id or file.filename == '':
        return jsonify({'status': 'error', 'message': 'Missing data'}), 400

    if file and allowed_file(file.filename, {'mp4', 'webm', 'ogg'}):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'videos', filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)

        video = Video(
            post_id=post_id,
            url=f'/static/uploads/videos/{filename}',
            filename=filename
        )
        db.session.add(video)
        db.session.commit()

        return jsonify({'status': 'success', 'video_id': video.id, 'shortcode': f'[video id={video.id}]'})

    return jsonify({'status': 'error', 'message': 'Invalid file type'}), 400


@bp.route('/api/upload_pdf', methods=['POST'])
@login_required
def upload_pdf():
    """Handle PDF upload."""
    if 'pdf' not in request.files:
        return jsonify({'status': 'error', 'message': 'No PDF file'}), 400

    file = request.files['pdf']
    post_id = request.form.get('post_id')

    if not post_id or file.filename == '':
        return jsonify({'status': 'error', 'message': 'Missing data'}), 400

    if file and allowed_file(file.filename, {'pdf'}):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'pdfs', filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)

        # Create a placeholder record for PDF (we'll extend this later)
        # For now, just return the URL
        pdf_url = f'/static/uploads/pdfs/{filename}'

        return jsonify({'status': 'success', 'pdf_url': pdf_url, 'shortcode': f'[pdf url="{pdf_url}"]'})

    return jsonify({'status': 'error', 'message': 'Invalid file type'}), 400


@bp.route('/api/log_quiz', methods=['POST'])
def log_quiz():
    """Log quiz interaction via AJAX."""
    data = request.get_json()
    quiz_id = data.get('quiz_id')
    event_type = data.get('event_type')  # 'attempt' or 'success'

    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({'status': 'error', 'message': 'Quiz not found'}), 404

    if event_type == 'attempt':
        quiz.attempts += 1
    elif event_type == 'success':
        quiz.successes += 1

    # Log analytics
    log_entry = AnalyticsLog(
        post_id=quiz.post_id,
        event_type=f'quiz_{event_type}',
        ip_address=request.remote_addr
    )
    db.session.add(log_entry)
    db.session.commit()

    return jsonify({'status': 'success'})


# Data fetching routes for interactive elements
@bp.route('/api/quiz/<int:quiz_id>')
def get_quiz(quiz_id):
    """Get quiz data for rendering."""
    quiz = Quiz.query.get_or_404(quiz_id)
    return jsonify({
        'id': quiz.id,
        'questions': quiz.questions,
        'attempts': quiz.attempts,
        'successes': quiz.successes
    })


@bp.route('/api/chart/<int:chart_id>')
def get_chart(chart_id):
    """Get chart data for rendering."""
    chart = Chart.query.get_or_404(chart_id)
    return jsonify(chart.data)


@bp.route('/api/video/<int:video_id>')
def get_video(video_id):
    """Get video data for rendering."""
    video = Video.query.get_or_404(video_id)
    return jsonify({
        'id': video.id,
        'url': video.url,
        'filename': video.filename
    })


@bp.route('/api/pdf/<int:pdf_id>')
def get_pdf(pdf_id):
    """Get PDF data for rendering."""
    # For now, we'll use a simple approach - this would need to be expanded
    # based on how PDFs are stored
    return jsonify({
        'id': pdf_id,
        'url': f'/static/uploads/pdfs/document_{pdf_id}.pdf'
    })


@bp.route('/api/dashboard/analytics')
@login_required
def dashboard_analytics():
    """Get analytics data for dashboard charts."""
    # Get post views over time (last 30 days)
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    # Aggregate views by date
    view_logs = AnalyticsLog.query.filter(
        AnalyticsLog.event_type == 'view',
        AnalyticsLog.timestamp >= thirty_days_ago
    ).all()

    views_by_date = {}
    for log in view_logs:
        date_key = log.timestamp.strftime('%Y-%m-%d')
        views_by_date[date_key] = views_by_date.get(date_key, 0) + 1

    # Get quiz statistics
    post_ids = [p.id for p in current_user.posts]
    quizzes = Quiz.query.filter(Quiz.post_id.in_(post_ids)).all()
    quiz_data = {
        'labels': [f'Quiz {q.id}' for q in quizzes],
        'attempts': [q.attempts for q in quizzes],
        'successes': [q.successes for q in quizzes]
    }

    return jsonify({
        'views': {
            'labels': list(views_by_date.keys()),
            'data': list(views_by_date.values())
        },
        'quiz': quiz_data
    })


# Admin Routes
@bp.route('/admin/users', methods=['GET', 'POST'])
@login_required
def admin_users():
    """Admin user management."""
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.dashboard'))

    form = UserForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User created successfully!', 'success')
        return redirect(url_for('main.admin_users'))

    users = User.query.all()
    return render_template('admin.html', form=form, users=users)


@bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
def admin_users_delete(user_id):
    """Delete user (admin only)."""
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.dashboard'))

    user = User.query.get_or_404(user_id)
    if user == current_user:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('main.admin_users'))

    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('main.admin_users'))


@bp.route('/admin/logins')
@login_required
def admin_logins():
    """View login attempt logs."""
    if current_user.role != 'admin':
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('main.dashboard'))

    logs = AnalyticsLog.query.filter(
        AnalyticsLog.event_type.in_(['login_success', 'login_failed'])
    ).order_by(AnalyticsLog.timestamp.desc()).limit(100).all()

    return render_template('admin.html', logs=logs, view='logins')
