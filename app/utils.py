import re
import json
import os
from werkzeug.utils import secure_filename
from bleach import clean
import google.generativeai as genai


def sanitize_input(text, allowed_tags=None):
    """
    Sanitize user input using Bleach to prevent XSS attacks.

    Args:
        text (str): Input text to sanitize
        allowed_tags (list): List of allowed HTML tags

    Returns:
        str: Sanitized text
    """
    if allowed_tags is None:
        allowed_tags = []

    # Basic HTML tags for rich text
    if not allowed_tags:
        allowed_tags = ['p', 'br', 'strong', 'b', 'em', 'i', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                       'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'a', 'img']

    allowed_attributes = {
        'a': ['href', 'title'],
        'img': ['src', 'alt', 'title'],
    }

    return clean(text, tags=allowed_tags, attributes=allowed_attributes, strip=True)


def parse_shortcodes(content):
    """
    Parse shortcodes in post content and replace with HTML placeholders.

    Args:
        content (str): Post content with shortcodes

    Returns:
        str: Content with shortcodes replaced by HTML elements
    """
    # Quiz shortcode: [quiz id=1]
    def replace_quiz(match):
        quiz_id = match.group(1)
        return f'<div class="interactive-quiz" data-quiz-id="{quiz_id}"></div>'

    content = re.sub(r'\[quiz id=(\d+)\]', replace_quiz, content)

    # Chart shortcode: [chart id=1]
    def replace_chart(match):
        chart_id = match.group(1)
        return f'<div class="interactive-chart" data-chart-id="{chart_id}"></div>'

    content = re.sub(r'\[chart id=(\d+)\]', replace_chart, content)

    # Video shortcode: [video id=1]
    def replace_video(match):
        video_id = match.group(1)
        return f'<div class="interactive-video" data-video-id="{video_id}"></div>'

    content = re.sub(r'\[video id=(\d+)\]', replace_video, content)

    # PDF shortcode: [pdf id=1]
    def replace_pdf(match):
        pdf_id = match.group(1)
        return f'<div class="interactive-pdf" data-pdf-id="{pdf_id}"></div>'

    content = re.sub(r'\[pdf id=(\d+)\]', replace_pdf, content)

    return content


def generate_tags_with_ai(post_content, api_key=None):
    """
    Generate categories and tags for a blog post using Google Gemini AI.

    Args:
        post_content (str): The blog post content
        api_key (str): Gemini API key (optional, will use env var if not provided)

    Returns:
        dict: {'categories': [...], 'tags': [...]}
    """
    if api_key is None:
        api_key = os.environ.get('GEMINI_API_KEY')

    if not api_key:
        # Fallback to basic keyword extraction if no API key
        return generate_basic_tags(post_content)

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')

        # Truncate content if too long
        truncated_content = post_content[:2000] if len(post_content) > 2000 else post_content

        prompt = f"""Analyze this blog post and generate exactly 3 categories and 5 tags.

Return ONLY valid JSON in this exact format:
{{"categories": ["category1", "category2", "category3"], "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]}}

Blog post content:
{truncated_content}"""

        response = model.generate_content(prompt)

        # Extract JSON from response
        response_text = response.text.strip()

        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            try:
                result = json.loads(json_match.group())
                return result
            except json.JSONDecodeError:
                pass

        # Fallback to basic extraction
        return generate_basic_tags(post_content)

    except Exception as e:
        print(f"Gemini API error: {e}")
        return generate_basic_tags(post_content)


def generate_basic_tags(post_content):
    """
    Basic keyword extraction as fallback when AI is not available.

    Args:
        post_content (str): The blog post content

    Returns:
        dict: Basic categories and tags
    """
    # Simple keyword-based extraction
    content_lower = post_content.lower()

    # Basic categories based on common topics
    categories = []
    if any(word in content_lower for word in ['code', 'programming', 'python', 'javascript', 'web']):
        categories.append('Technology')
    if any(word in content_lower for word in ['tutorial', 'guide', 'how to']):
        categories.append('Tutorial')
    if any(word in content_lower for word in ['opinion', 'thoughts', 'perspective']):
        categories.append('Opinion')

    # If no categories found, add general ones
    if not categories:
        categories = ['General', 'Blog']

    # Extract some basic tags from common words
    common_words = ['web', 'development', 'python', 'javascript', 'tutorial', 'guide', 'tips', 'tricks']
    tags = [word for word in common_words if word in content_lower][:5]

    # If no tags found, add some defaults
    if not tags:
        tags = ['blog', 'article', 'post']

    return {
        'categories': categories,
        'tags': tags
    }


def secure_filename_custom(filename):
    """
    Sanitize filename for secure file uploads.

    Args:
        filename (str): Original filename

    Returns:
        str: Sanitized filename
    """
    return secure_filename(filename)


def allowed_file(filename, allowed_extensions):
    """
    Check if file extension is allowed.

    Args:
        filename (str): Filename to check
        allowed_extensions (set): Set of allowed extensions (without dots)

    Returns:
        bool: True if allowed, False otherwise
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def get_file_extension(filename):
    """
    Get file extension from filename.

    Args:
        filename (str): Filename

    Returns:
        str: File extension (lowercase)
    """
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''


def truncate_text(text, max_length=100):
    """
    Truncate text to specified length with ellipsis.

    Args:
        text (str): Text to truncate
        max_length (int): Maximum length

    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + '...'
