import pytest
from unittest.mock import patch
import sys
import os

# Add the parent directory to sys.path so we can import devdoc
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from devdoc.cli import main


def test_devdoc_help_command():
    """Test that devdoc --help works"""
    with patch('sys.argv', ['devdoc', '--help']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0


def test_devdoc_init_command():
    """Test that devdoc init works"""
    with patch('sys.argv', ['devdoc', 'init']):
        # Should not raise an exception
        result = main()
        assert result is None  # Successful execution returns None


def test_devdoc_no_args_shows_help():
    """Test that devdoc with no args shows help"""
    with patch('sys.argv', ['devdoc']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        # Should exit with non-zero code when no command given
        assert exc_info.value.code != 0