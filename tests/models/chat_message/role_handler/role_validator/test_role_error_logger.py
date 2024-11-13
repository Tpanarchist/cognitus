"""Tests for role error logging functionality"""
import pytest
import logging
from models.chat_message.role_handler.role_validator import RoleErrorLogger

@pytest.fixture
def role_logger(caplog):
    """Fixture providing RoleErrorLogger instance with captured logs"""
    caplog.set_level(logging.ERROR)
    return RoleErrorLogger()

def test_log_invalid_role(role_logger, caplog):
    """Test logging of invalid role"""
    role_logger.log_invalid_role("invalid_role")
    assert "Invalid role 'invalid_role' provided" in caplog.text

def test_log_invalid_role_with_context(role_logger, caplog):
    """Test logging of invalid role with context"""
    role_logger.log_invalid_role("invalid_role", "test context")
    assert "Invalid role 'invalid_role' provided in test context" in caplog.text