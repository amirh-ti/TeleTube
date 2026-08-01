import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.helpers import extract_video_id, sanitize_filename, progress_bar
from utils.validators import is_valid_youtube_url


def test_extract_video_id_watch_url():
    assert extract_video_id("https://www.youtube.com/watch?v=abc123") == "abc123"


def test_extract_video_id_short_url():
    assert extract_video_id("https://youtu.be/abc123") == "abc123"


def test_extract_video_id_invalid():
    assert extract_video_id("https://example.com") is None


def test_sanitize_filename():
    assert sanitize_filename('a/b:c*d?e"f<g>h|i') == "a_b_c_d_e_f_g_h_i"


def test_progress_bar_bounds():
    assert progress_bar(0) == "-" * 12
    assert progress_bar(100) == "#" * 12
    assert progress_bar(150) == "#" * 12  # clamp بالای ۱۰۰
    assert progress_bar(-10) == "-" * 12  # clamp زیر ۰


def test_is_valid_youtube_url():
    assert is_valid_youtube_url("https://youtu.be/abc123")
    assert is_valid_youtube_url("https://www.youtube.com/watch?v=abc123")
    assert not is_valid_youtube_url("https://example.com")
