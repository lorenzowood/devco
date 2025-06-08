import pytest
from unittest.mock import patch
import sys
import os

# Add the parent directory to sys.path so we can import devco
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from devco.cli import main


def test_devco_help_command():
    """Test that devco --help works"""
    with patch('sys.argv', ['devco', '--help']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0


def test_devco_init_command():
    """Test that devco init works"""
    with patch('sys.argv', ['devco', 'init']):
        # Should not raise an exception
        result = main()
        assert result is None  # Successful execution returns None


def test_devco_no_args_shows_help():
    """Test that devco with no args shows help"""
    with patch('sys.argv', ['devco']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        # Should exit with non-zero code when no command given
        assert exc_info.value.code != 0