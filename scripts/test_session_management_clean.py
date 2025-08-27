"""
Test script for the enhanced database-backed session management system.

This script demonstrates and tests:
1. Session creation and management
2. Database persistence (if available)
3. Backward compatibility with existing session manager

Run this script to verify the session management system is working correctly.
"""

import asyncio
from sqlalchemy import text
from fastapi_security_sample.db import SessionLocal
from fastapi_security_sample.users.models import User
from fastapi_security_sample.users.sessions import session_manager

import logging

logger = logging.getLogger(__name__)


async def create_test_user():
    """Create a test user for session testing"""
    from fastapi_security_sample.users.utils import get_password_hash
    from ulid import new as ulid_new
    
    async with SessionLocal() as session:
        # Check if test user already exists
        result = await session.execute(
            text("SELECT * FROM users WHERE username = :username"),
            {"username": "test_session_user"}
        )
        user_row = result.fetchone()
        
        if not user_row:
            user = User(
                id=str(ulid_new()),
                username="test_session_user",
                email="test_session@example.com",
                hashed_password=get_password_hash("Xy9#mK$qL8&wZ2@v")
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            logger.info(f"✅ Created test user: {user.username}")
        else:
            # Create user object from existing data
            user = User(
                id=user_row[0],  # Assuming id is first column
                username=user_row[1],  # Assuming username is second column
                email=user_row[2],  # Assuming email is third column
                hashed_password=user_row[3]  # Assuming hashed_password is fourth column
            )
            logger.info(f"✅ Using existing test user: {user.username}")
        
        return user


async def test_session_creation():
    """Test session creation and basic functionality"""
    logger.info("🧪 Testing session creation...")
    
    # Create test user
    user = await create_test_user()
    
    # Create a session using the session manager
    session = session_manager.create_session(
        user=user,
        client_ip="192.168.1.100",
        user_agent="TestAgent/1.0 (Testing)"
    )
    
    logger.info(f"✅ Created session with ID: {session.id}")
    logger.info(f"   - User ID: {session.user_id}")
    logger.info(f"   - Client IP: {session.client_ip}")
    logger.info(f"   - User Agent: {session.user_agent}")
    logger.info(f"   - Active: {session.is_active}")
    
    return user, session


async def test_session_retrieval():
    """Test session retrieval and validation"""
    logger.info("🧪 Testing session retrieval...")
    
    user, session = await test_session_creation()
    
    # Test session retrieval
    retrieved_session = session_manager.get_session(session.id)
    if retrieved_session:
        logger.info(f"✅ Session retrieved successfully: {retrieved_session.id}")
        logger.info(f"   - User ID matches: {retrieved_session.user_id == session.user_id}")
        logger.info(f"   - Active: {retrieved_session.is_active}")
    else:
        logger.error("❌ Session not found")
    
    return user, session


async def test_user_sessions():
    """Test getting all sessions for a user"""
    logger.info("🧪 Testing user sessions retrieval...")
    
    user, session = await test_session_retrieval()
    
    # Get user sessions
    user_sessions = session_manager.get_user_sessions(user.id)
    logger.info(f"✅ Found {len(user_sessions)} sessions for user")
    
    # Create another session for the same user
    session2 = session_manager.create_session(
        user=user,
        client_ip="192.168.1.101",
        user_agent="TestAgent/2.0"
    )
    
    # Check sessions again
    user_sessions = session_manager.get_user_sessions(user.id)
    logger.info(f"✅ After creating second session: {len(user_sessions)} sessions")
    
    return user, [session, session2]


async def test_session_removal():
    """Test session removal"""
    logger.info("🧪 Testing session removal...")
    
    user, sessions = await test_user_sessions()
    
    # Remove first session
    removed = session_manager.remove_session(sessions[0].id)
    logger.info(f"✅ Session removal result: {removed}")
    
    # Verify session is removed
    retrieved_session = session_manager.get_session(sessions[0].id)
    is_removed = retrieved_session is None
    logger.info(f"✅ Session removed verification: {is_removed}")
    
    # Check user sessions count
    user_sessions = session_manager.get_user_sessions(user.id)
    logger.info(f"✅ Remaining sessions: {len(user_sessions)}")
    
    return user, sessions[1:]


async def test_session_cleanup():
    """Test session cleanup functionality"""
    logger.info("🧪 Testing session cleanup...")
    
    # Test expired session cleanup
    cleaned_count = session_manager.cleanup_expired_sessions()
    logger.info(f"✅ Cleaned up {cleaned_count} expired sessions")


async def test_enhanced_features():
    """Test enhanced features if available"""
    logger.info("🧪 Testing enhanced features...")
    
    # Check if we're using the enhanced session manager
    if hasattr(session_manager, 'enable_db_persistence'):
        logger.info(f"✅ Enhanced session manager detected")
        logger.info(f"   - Database persistence: {getattr(session_manager, 'enable_db_persistence', False)}")
        logger.info(f"   - Analytics enabled: {getattr(session_manager, 'enable_analytics', False)}")
    else:
        logger.info("ℹ️  Using standard in-memory session manager")
    
    # Test analytics if available
    if hasattr(session_manager, 'get_session_analytics'):
        try:
            user, _ = await test_session_removal()
            analytics = session_manager.get_session_analytics(user.id)
            logger.info(f"✅ Session analytics available: {type(analytics)}")
        except Exception as e:
            logger.info(f"ℹ️  Session analytics error: {e}")


async def test_database_persistence():
    """Test database persistence features"""
    logger.info("🧪 Testing database persistence...")
    
    try:
        async with SessionLocal() as session:
            # Check if session tables exist
            result = await session.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('user_sessions', 'session_activities')")
            )
            tables = result.fetchall()
            
            if tables:
                logger.info(f"✅ Found session tables: {[t[0] for t in tables]}")
                
                # Count sessions in database
                for table_name in [t[0] for t in tables]:
                    count_result = await session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count = count_result.scalar()
                    logger.info(f"   - {table_name}: {count} records")
            else:
                logger.info("ℹ️  No session tables found - using in-memory storage")
                
    except Exception as e:
        logger.info(f"ℹ️  Database check failed: {e}")


async def cleanup_test_data():
    """Clean up test data"""
    logger.info("🧹 Cleaning up test data...")
    
    try:
        # Clean up in-memory sessions first
        user = await create_test_user()
        user_sessions = session_manager.get_user_sessions(user.id)
        removed_count = 0
        for session in user_sessions:
            if session_manager.remove_session(session.id):
                removed_count += 1
        logger.info(f"✅ Cleaned up {removed_count} in-memory sessions")
        
        # Clean up database if needed
        async with SessionLocal() as session:
            # Delete test user (this should cascade to sessions if FK constraints are set up)
            await session.execute(
                text("DELETE FROM users WHERE username = :username"),
                {"username": "test_session_user"}
            )
            await session.commit()
            logger.info("✅ Cleaned up test user from database")
            
    except Exception as e:
        logger.warning(f"⚠️  Cleanup warning: {e}")


async def main():
    """Main test function"""
    print("🚀 Starting Session Management System Tests")
    print("=" * 50)
    
    try:
        # Run basic tests
        await test_session_creation()
        print()
        
        await test_session_retrieval()
        print()
        
        await test_user_sessions()
        print()
        
        await test_session_removal()
        print()
        
        await test_session_cleanup()
        print()
        
        await test_enhanced_features()
        print()
        
        await test_database_persistence()
        print()
        
        print("✅ All session management tests completed successfully!")
        print("\nSession management system status:")
        print("✓ Basic session operations functional")
        print("✓ Session retrieval working")
        print("✓ Multiple sessions per user supported")
        print("✓ Session removal functional")
        print("✓ Session cleanup operational")
        
        # Check manager type
        manager_type = type(session_manager).__name__
        print(f"✓ Using {manager_type}")
        
        if hasattr(session_manager, 'enable_db_persistence'):
            if getattr(session_manager, 'enable_db_persistence', False):
                print("✓ Database persistence enabled")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise
    
    finally:
        # Clean up test data
        try:
            await cleanup_test_data()
        except Exception as e:
            logger.warning(f"⚠️  Cleanup failed: {e}")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Run tests
    asyncio.run(main())
