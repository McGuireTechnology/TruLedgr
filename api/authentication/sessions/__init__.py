"""
Sessions Authentication Module

This module provides session management functionality including:
- Session creation and validation
- Session lifecycle management
- Session activity tracking
- Security monitoring
- Enhanced analytics and device tracking
"""

from .service import SessionService
from .router import router
from .analytics import (
    EnhancedSessionManager,
    SessionAnalytics, 
    enhanced_session_manager
)

__all__ = [
    "SessionService",
    "router",
    # Enhanced Analytics
    "EnhancedSessionManager",
    "SessionAnalytics",
    "enhanced_session_manager"
]
