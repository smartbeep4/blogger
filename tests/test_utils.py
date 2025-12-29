import pytest
from app.utils import (
    sanitize_input, parse_shortcodes, generate_basic_tags,
    allowed_file, secure_filename_custom, truncate_text
)


class TestSanitization:
    """Test input sanitization functions."""

    def test_sanitize_input_basic(self):
        """Test basic HTML sanitization."""
        input_html = '<p>Hello <strong>world</strong></p>'
        result = sanitize_input(input_html, ['p', 'strong'])
        assert '<p>' in result
        assert '<strong>' in result
        assert result == input_html

    def test_sanitize_input_removes_dangerous(self):
        """Test removal of dangerous HTML tags."""
        dangerous_html = '<script>alert("xss")</script><p>Safe content</p>'
        result = sanitize_input(dangerous_html, ['p'])
        assert '<script>' not in result
        assert '<p>Safe content</p>' in result

    def test_sanitize_input_strips(self):
        """Test HTML stripping."""
        html = '<p>Some <em>emphasized</em> text</p>'
        result = sanitize_input(html, [])  # No allowed tags
        assert '<p>' not in result
        assert '<em>' not in result
        assert result == 'Some emphasized text'


class TestShortcodeParsing:
    """Test shortcode parsing functionality."""

    def test_parse_quiz_shortcode(self):
        """Test quiz shortcode parsing."""
        content = 'Here is a quiz: [quiz id=1]'
        result = parse_shortcodes(content)
        expected = 'Here is a quiz: <div class="interactive-quiz" data-quiz-id="1"></div>'
        assert result == expected

    def test_parse_chart_shortcode(self):
        """Test chart shortcode parsing."""
        content = 'Chart: [chart id=2]'
        result = parse_shortcodes(content)
        expected = 'Chart: <div class="interactive-chart" data-chart-id="2"></div>'
        assert result == expected

    def test_parse_video_shortcode(self):
        """Test video shortcode parsing."""
        content = 'Video: [video id=3]'
        result = parse_shortcodes(content)
        expected = 'Video: <div class="interactive-video" data-video-id="3"></div>'
        assert result == expected

    def test_parse_pdf_shortcode(self):
        """Test PDF shortcode parsing."""
        content = 'PDF: [pdf id=4]'
        result = parse_shortcodes(content)
        expected = 'PDF: <div class="interactive-pdf" data-pdf-id="4"></div>'
        assert result == expected

    def test_parse_multiple_shortcodes(self):
        """Test parsing multiple shortcodes in content."""
        content = 'Quiz: [quiz id=1] Chart: [chart id=2] Video: [video id=3]'
        result = parse_shortcodes(content)
        assert 'data-quiz-id="1"' in result
        assert 'data-chart-id="2"' in result
        assert 'data-video-id="3"' in result


class TestTagGeneration:
    """Test tag generation functionality."""

    def test_generate_basic_tags_technology(self):
        """Test basic tag generation for technology content."""
        content = 'Python Flask web development tutorial programming code'
        result = generate_basic_tags(content)

        assert 'categories' in result
        assert 'tags' in result
        assert isinstance(result['categories'], list)
        assert isinstance(result['tags'], list)

    def test_generate_basic_tags_tutorial(self):
        """Test basic tag generation for tutorial content."""
        content = 'How to build a web app step by step guide tutorial'
        result = generate_basic_tags(content)

        assert len(result['categories']) > 0
        assert len(result['tags']) > 0

    def test_generate_basic_tags_empty(self):
        """Test basic tag generation with minimal content."""
        content = 'Some random text without keywords'
        result = generate_basic_tags(content)

        # Should still return some default tags
        assert 'categories' in result
        assert 'tags' in result


class TestFileHandling:
    """Test file handling utilities."""

    def test_allowed_file_valid(self):
        """Test allowed file type checking."""
        assert allowed_file('document.pdf', {'pdf'})
        assert allowed_file('video.mp4', {'mp4', 'webm', 'ogg'})
        assert allowed_file('image.jpg', {'jpg', 'png'})

    def test_allowed_file_invalid(self):
        """Test invalid file type checking."""
        assert not allowed_file('script.exe', {'pdf'})
        assert not allowed_file('document.txt', {'pdf'})
        assert not allowed_file('image.gif', {'jpg', 'png'})

    def test_allowed_file_no_extension(self):
        """Test file without extension."""
        assert not allowed_file('document', {'pdf'})

    def test_secure_filename_custom(self):
        """Test filename sanitization."""
        # This would use Werkzeug's secure_filename
        result = secure_filename_custom('safe-file.pdf')
        assert result == 'safe-file.pdf'

        # Test with potentially unsafe characters
        unsafe = secure_filename_custom('unsafe/../file.pdf')
        assert '..' not in unsafe


class TestTextUtilities:
    """Test text utility functions."""

    def test_truncate_text_short(self):
        """Test truncating short text."""
        text = 'Short text'
        result = truncate_text(text, 20)
        assert result == text

    def test_truncate_text_long(self):
        """Test truncating long text."""
        text = 'This is a very long text that should be truncated'
        result = truncate_text(text, 20)
        assert len(result) <= 23  # 20 + 3 for '...'
        assert result.endswith('...')

    def test_truncate_text_exact(self):
        """Test truncating text at exact length."""
        text = 'Exactly twenty chars'
        result = truncate_text(text, 20)
        assert result == text
