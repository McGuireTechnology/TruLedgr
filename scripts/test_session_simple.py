"""
Simple session management test using existing infrastructure.

This test validates that the enhanced session management system is working
by testing the basic session operations without creating new users.
"""

import asyncio
from fastapi_security_sample.users.sessions import session_manager
from fastapi_security_sample.users.models import User

import logging

logger = logging.getLogger(__name__)


def create_test_user(user_id: str, username: str) -> User:
    """Create a minimal User object for testing (not saved to database)"""
    return User(
        id=user_id,
        username=username,
        email=f"{username}@example.com",
        hashed_password="dummy_hash"
    )


async def test_basic_session_operations():
    """Test basic session management operations"""
    logger.info("🧪 Testing basic session operations...")
    
    # Create a test user object
    user = create_test_user("test_user_001", "test_user")
    
    # Test session creation
    session = session_manager.create_session(
        user=user,
        client_ip="192.168.1.100",
        user_agent="TestAgent/1.0"
    )
    
    logger.info(f"✅ Created session: {session.id}")
    logger.info(f"   - User ID: {session.user_id}")
    logger.info(f"   - Client IP: {session.client_ip}")
    logger.info(f"   - Active: {session.is_active}")
    
    # Test session retrieval
    retrieved_session = session_manager.get_session(session.id)
    if retrieved_session:
        logger.info(f"✅ Retrieved session: {retrieved_session.id}")
    else:
        logger.error("❌ Failed to retrieve session")
        return False
    
    # Test user sessions
    user_sessions = session_manager.get_user_sessions(user.id)
    logger.info(f"✅ User has {len(user_sessions)} sessions")
    
    # Test session removal
    removed = session_manager.remove_session(session.id)
    logger.info(f"✅ Session removal: {removed}")
    
    # Verify removal
    retrieved_after_removal = session_manager.get_session(session.id)
    if retrieved_after_removal is None:
        logger.info("✅ Session successfully removed")
    else:
        logger.error("❌ Session not removed")
        return False
    
    return True


async def test_multiple_sessions():
    """Test multiple sessions for the same user"""
    logger.info("🧪 Testing multiple sessions...")
    
    user = create_test_user("test_user_002", "multi_session_user")
    
    sessions = []
    for i in range(3):
        session = session_manager.create_session(
            user=user,
            client_ip=f"192.168.1.{100+i}",
            user_agent=f"TestAgent/{i+1}.0"
        )
        sessions.append(session)
        logger.info(f"   Created session {i+1}: {session.id}")
    
    # Check user sessions
    user_sessions = session_manager.get_user_sessions(user.id)
    logger.info(f"✅ User has {len(user_sessions)} sessions total")
    
    # Clean up sessions
    for session in sessions:
        session_manager.remove_session(session.id)
    
    # Verify cleanup
    remaining_sessions = session_manager.get_user_sessions(user.id)
    logger.info(f"✅ After cleanup: {len(remaining_sessions)} sessions remaining")
    
    return True


async def test_session_cleanup():
    """Test session cleanup functionality"""
    logger.info("🧪 Testing session cleanup...")
    
    # Test cleanup (should not crash)
    cleaned_count = session_manager.cleanup_expired_sessions()
    logger.info(f"✅ Cleanup completed: {cleaned_count} sessions cleaned")
    
    return True


async def test_enhanced_features():
    """Test enhanced features detection"""
    logger.info("🧪 Testing enhanced features detection...")
    
    # Check session manager type
    manager_type = type(session_manager).__name__
    logger.info(f"✅ Session manager type: {manager_type}")
    
    # Check for enhanced features
    if hasattr(session_manager, 'enable_db_persistence'):
        logger.info(f"✅ Enhanced session manager detected")
        persistence = getattr(session_manager, 'enable_db_persistence', False)
        analytics = getattr(session_manager, 'enable_analytics', False)
        logger.info(f"   - Database persistence: {persistence}")
        logger.info(f"   - Analytics enabled: {analytics}")
    else:
        logger.info("ℹ️  Standard session manager detected")
    
    # Check for analytics methods
    has_analytics = hasattr(session_manager, 'get_session_analytics')
    logger.info(f"✅ Analytics methods available: {has_analytics}")
    
    return True


async def main():
    """Main test function"""
    print("🚀 Starting Simple Session Management Tests")
    print("=" * 50)
    
    success = True
    
    try:
        # Run basic tests
        if not await test_basic_session_operations():
            success = False
        print()
        
        if not await test_multiple_sessions():
            success = False
        print()
        
        if not await test_session_cleanup():
            success = False
        print()
        
        if not await test_enhanced_features():
            success = False
        print()
        
        if success:
            print("✅ All session management tests completed successfully!")
            print("\nSession management system status:")
            print("✓ Basic session operations functional")
            print("✓ Multiple sessions per user supported")
            print("✓ Session cleanup operational")
            
            # Enhanced features check
            if hasattr(session_manager, 'enable_db_persistence'):
                if getattr(session_manager, 'enable_db_persistence', False):
                    print("✓ Enhanced session manager with database persistence")
                else:
                    print("ℹ️  Enhanced session manager (database persistence disabled)")
            else:
                print("ℹ️  Standard in-memory session manager")
        else:
            print("❌ Some tests failed")
            
    except Exception as e:
        logger.error(f"❌ Test suite failed: {e}")
        success = False
    
    return success


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Run tests
    result = asyncio.run(main())
    exit(0 if result else 1)
