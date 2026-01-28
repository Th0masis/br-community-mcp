"""Tests for utility functions."""

from src.utils import strip_html


class TestStripHtml:
    """Tests for the strip_html function."""

    def test_removes_simple_tags(self) -> None:
        """Test that simple HTML tags are removed."""
        html = "<p>Hello World</p>"
        result = strip_html(html)
        assert result == "Hello World"

    def test_removes_nested_tags(self) -> None:
        """Test that nested HTML tags are removed."""
        html = "<div><p><strong>Bold</strong> text</p></div>"
        result = strip_html(html)
        assert result == "Bold text"

    def test_decodes_amp_entity(self) -> None:
        """Test that &amp; is decoded to &."""
        html = "Tom &amp; Jerry"
        result = strip_html(html)
        assert result == "Tom & Jerry"

    def test_decodes_lt_gt_entities(self) -> None:
        """Test that &lt; and &gt; are decoded."""
        html = "&lt;code&gt;"
        result = strip_html(html)
        assert result == "<code>"

    def test_decodes_quot_entity(self) -> None:
        """Test that &quot; is decoded to double quote."""
        html = "He said &quot;Hello&quot;"
        result = strip_html(html)
        assert result == 'He said "Hello"'

    def test_decodes_apos_entity(self) -> None:
        """Test that &#39; is decoded to single quote."""
        html = "It&#39;s working"
        result = strip_html(html)
        assert result == "It's working"

    def test_decodes_nbsp_entity(self) -> None:
        """Test that &nbsp; is decoded to space."""
        html = "Hello&nbsp;World"
        result = strip_html(html)
        assert result == "Hello World"

    def test_normalizes_whitespace(self) -> None:
        """Test that multiple whitespaces are normalized."""
        html = "<p>Hello</p>   <p>World</p>"
        result = strip_html(html)
        assert result == "Hello World"

    def test_strips_leading_trailing_whitespace(self) -> None:
        """Test that leading/trailing whitespace is stripped."""
        html = "  <p>Hello</p>  "
        result = strip_html(html)
        assert result == "Hello"

    def test_handles_empty_string(self) -> None:
        """Test that empty string returns empty string."""
        result = strip_html("")
        assert result == ""

    def test_handles_plain_text(self) -> None:
        """Test that plain text without HTML is unchanged."""
        text = "Just plain text"
        result = strip_html(text)
        assert result == "Just plain text"

    def test_complex_html(self) -> None:
        """Test complex HTML with multiple entities and tags."""
        html = '<div class="content"><p>Hello &amp; <strong>World</strong>!</p></div>'
        result = strip_html(html)
        assert result == "Hello & World !"
