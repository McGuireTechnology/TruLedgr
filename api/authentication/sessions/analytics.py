"""
Enhanced Session Manager

Provides advanced session management with analytics, device tracking,
and security monitoring capabilities.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlmodel import SQLModel, Field, select, desc
from sqlmodel.ext.asyncio.session import AsyncSession

from api.settings import get_settings


class SessionAnalytics(SQLModel, table=True):
    """Database model for session analytics"""
    
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(index=True)
    user_id: str = Field(foreign_key="users.id", index=True)
    
    # Device and location info
    device_type: Optional[str] = None  # mobile, desktop, tablet
    browser: Optional[str] = None
    os: Optional[str] = None
    ip_address: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    
    # Session metrics
    login_time: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    logout_time: Optional[datetime] = None
    session_duration: Optional[int] = None  # in seconds
    
    # Activity tracking
    page_views: int = Field(default=0)
    api_calls: int = Field(default=0)
    last_page: Optional[str] = None
    last_endpoint: Optional[str] = None
    
    # Security flags
    is_suspicious: bool = Field(default=False)
    security_score: int = Field(default=100)  # 0-100, lower is more suspicious
    failed_actions: int = Field(default=0)


class EnhancedSessionManager:
    """
    Enhanced session manager with comprehensive analytics and monitoring.
    
    Features:
    - Device and browser detection
    - Geographic tracking
    - Activity monitoring
    - Security scoring
    - Session analytics
    - Anomaly detection
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.max_sessions_per_user = getattr(self.settings, 'max_sessions_per_user', 10)
        self.session_timeout_hours = getattr(self.settings, 'session_timeout_hours', 24)
        self.activity_timeout_minutes = getattr(self.settings, 'activity_timeout_minutes', 30)
    
    async def create_session_analytics(
        self,
        session: AsyncSession,
        session_id: str,
        user_id: str,
        request_info: Dict[str, Any]
    ) -> SessionAnalytics:
        """Create session analytics record"""
        
        # Parse user agent (simplified without external library)
        user_agent_str = request_info.get('user_agent', '')
        
        # Simple device detection
        device_type = "desktop"
        if any(mobile in user_agent_str.lower() for mobile in ['mobile', 'android', 'iphone']):
            device_type = "mobile"
        elif any(tablet in user_agent_str.lower() for tablet in ['tablet', 'ipad']):
            device_type = "tablet"
        
        # Simple browser detection
        browser = "Unknown"
        if 'chrome' in user_agent_str.lower():
            browser = "Chrome"
        elif 'firefox' in user_agent_str.lower():
            browser = "Firefox"
        elif 'safari' in user_agent_str.lower():
            browser = "Safari"
        elif 'edge' in user_agent_str.lower():
            browser = "Edge"
        
        # Simple OS detection
        os_name = "Unknown"
        if 'windows' in user_agent_str.lower():
            os_name = "Windows"
        elif 'mac' in user_agent_str.lower():
            os_name = "macOS"
        elif 'linux' in user_agent_str.lower():
            os_name = "Linux"
        elif 'android' in user_agent_str.lower():
            os_name = "Android"
        elif 'ios' in user_agent_str.lower():
            os_name = "iOS"
        
        # Create analytics record
        analytics = SessionAnalytics(
            session_id=session_id,
            user_id=user_id,
            device_type=device_type,
            browser=browser,
            os=os_name,
            ip_address=request_info.get('client_ip'),
            # Geographic info would be populated by IP geolocation service
            country=request_info.get('country'),
            city=request_info.get('city')
        )
        
        session.add(analytics)
        await session.commit()
        await session.refresh(analytics)
        
        return analytics
    
    async def update_session_activity(
        self,
        session: AsyncSession,
        session_id: str,
        activity_data: Dict[str, Any]
    ) -> None:
        """Update session activity metrics"""
        
        query = select(SessionAnalytics).where(
            SessionAnalytics.session_id == session_id,
            SessionAnalytics.logout_time == None
        )
        result = await session.execute(query)
        analytics = result.scalar_one_or_none()
        
        if not analytics:
            return
        
        # Update activity
        analytics.last_activity = datetime.utcnow()
        
        if activity_data.get('page_view'):
            analytics.page_views += 1
            analytics.last_page = activity_data.get('page')
        
        if activity_data.get('api_call'):
            analytics.api_calls += 1
            analytics.last_endpoint = activity_data.get('endpoint')
        
        # Update security score based on activity
        await self._update_security_score(analytics, activity_data)
        
        await session.commit()
    
    async def end_session(
        self,
        session: AsyncSession,
        session_id: str,
        logout_reason: str = "user_logout"
    ) -> None:
        """End session and calculate final metrics"""
        
        query = select(SessionAnalytics).where(
            SessionAnalytics.session_id == session_id,
            SessionAnalytics.logout_time == None
        )
        result = await session.execute(query)
        analytics = result.scalar_one_or_none()
        
        if not analytics:
            return
        
        # Calculate session duration
        logout_time = datetime.utcnow()
        duration = int((logout_time - analytics.login_time).total_seconds())
        
        analytics.logout_time = logout_time
        analytics.session_duration = duration
        
        await session.commit()
        
        # Log session end event
        await self._log_session_event(
            session, "session_ended", {
                "session_id": session_id,
                "user_id": analytics.user_id,
                "duration": duration,
                "logout_reason": logout_reason,
                "page_views": analytics.page_views,
                "api_calls": analytics.api_calls
            }
        )
    
    async def get_user_sessions(
        self,
        session: AsyncSession,
        user_id: str,
        active_only: bool = True
    ) -> List[SessionAnalytics]:
        """Get all sessions for a user"""
        
        query = select(SessionAnalytics).where(
            SessionAnalytics.user_id == user_id
        )
        
        if active_only:
            query = query.where(SessionAnalytics.logout_time == None)
        
        query = query.order_by(desc(SessionAnalytics.login_time))
        
        result = await session.execute(query)
        return list(result.scalars().all())
    
    async def get_session_analytics(
        self,
        session: AsyncSession,
        session_id: str
    ) -> Optional[SessionAnalytics]:
        """Get analytics for a specific session"""
        
        query = select(SessionAnalytics).where(
            SessionAnalytics.session_id == session_id
        )
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_user_analytics_summary(
        self,
        session: AsyncSession,
        user_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get analytics summary for a user"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        query = select(SessionAnalytics).where(
            SessionAnalytics.user_id == user_id,
            SessionAnalytics.login_time >= cutoff_date
        )
        result = await session.execute(query)
        sessions = result.scalars().all()
        
        if not sessions:
            return {
                "total_sessions": 0,
                "total_duration": 0,
                "avg_duration": 0,
                "total_page_views": 0,
                "total_api_calls": 0,
                "devices_used": [],
                "browsers_used": [],
                "countries": [],
                "suspicious_sessions": 0
            }
        
        # Calculate metrics
        total_duration = sum(s.session_duration or 0 for s in sessions)
        completed_sessions = [s for s in sessions if s.session_duration is not None]
        avg_duration = total_duration / len(completed_sessions) if completed_sessions else 0
        
        # Collect unique values
        devices = list(set(s.device_type for s in sessions if s.device_type))
        browsers = list(set(s.browser for s in sessions if s.browser))
        countries = list(set(s.country for s in sessions if s.country))
        
        return {
            "total_sessions": len(sessions),
            "active_sessions": len([s for s in sessions if s.logout_time is None]),
            "total_duration": total_duration,
            "avg_duration": avg_duration,
            "total_page_views": sum(s.page_views for s in sessions),
            "total_api_calls": sum(s.api_calls for s in sessions),
            "devices_used": devices,
            "browsers_used": browsers,
            "countries": countries,
            "suspicious_sessions": len([s for s in sessions if s.is_suspicious]),
            "avg_security_score": sum(s.security_score for s in sessions) / len(sessions)
        }
    
    async def detect_suspicious_activity(
        self,
        session: AsyncSession,
        user_id: str
    ) -> List[Dict[str, Any]]:
        """Detect suspicious session activity"""
        
        # Get recent sessions (last 7 days)
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        
        query = select(SessionAnalytics).where(
            SessionAnalytics.user_id == user_id,
            SessionAnalytics.login_time >= cutoff_date
        )
        result = await session.execute(query)
        sessions = result.scalars().all()
        
        suspicious_activities = []
        
        # Check for multiple devices
        devices = set(s.device_type for s in sessions if s.device_type)
        if len(devices) > 3:
            suspicious_activities.append({
                "type": "multiple_devices",
                "description": f"User accessed from {len(devices)} different device types",
                "severity": "medium"
            })
        
        # Check for multiple countries
        countries = set(s.country for s in sessions if s.country)
        if len(countries) > 2:
            suspicious_activities.append({
                "type": "multiple_locations",
                "description": f"User accessed from {len(countries)} different countries",
                "severity": "high"
            })
        
        # Check for unusual activity patterns
        for session_analytics in sessions:
            if session_analytics.security_score < 50:
                suspicious_activities.append({
                    "type": "low_security_score",
                    "description": f"Session has low security score: {session_analytics.security_score}",
                    "severity": "medium",
                    "session_id": session_analytics.session_id
                })
        
        # Check for rapid successive logins
        login_times = [s.login_time for s in sessions]
        login_times.sort()
        
        for i in range(1, len(login_times)):
            if (login_times[i] - login_times[i-1]).total_seconds() < 60:
                suspicious_activities.append({
                    "type": "rapid_logins",
                    "description": "Multiple logins within 1 minute",
                    "severity": "high"
                })
                break
        
        return suspicious_activities
    
    async def cleanup_old_sessions(
        self,
        session: AsyncSession,
        days_old: int = 90
    ) -> int:
        """Clean up old session analytics data"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        query = select(SessionAnalytics).where(
            SessionAnalytics.login_time < cutoff_date
        )
        result = await session.execute(query)
        old_sessions = result.scalars().all()
        
        count = len(old_sessions)
        
        for session_analytics in old_sessions:
            await session.delete(session_analytics)
        
        await session.commit()
        
        return count
    
    async def _update_security_score(
        self,
        analytics: SessionAnalytics,
        activity_data: Dict[str, Any]
    ) -> None:
        """Update security score based on activity"""
        
        # Decrease score for failed actions
        if activity_data.get('failed_action'):
            analytics.failed_actions += 1
            analytics.security_score = max(0, analytics.security_score - 5)
        
        # Decrease score for suspicious patterns
        if activity_data.get('suspicious_pattern'):
            analytics.security_score = max(0, analytics.security_score - 10)
        
        # Mark as suspicious if score gets too low
        if analytics.security_score < 50:
            analytics.is_suspicious = True
    
    async def _log_session_event(
        self,
        session: AsyncSession,
        event_type: str,
        details: Dict[str, Any]
    ) -> None:
        """Log session events"""
        timestamp = int(time.time())
        print(f"[SESSION_ANALYTICS] {timestamp}: {event_type} - {details}")


# Global enhanced session manager instance
enhanced_session_manager = EnhancedSessionManager()
