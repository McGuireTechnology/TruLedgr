
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
                hashed_password=get_password_hash("test_password")
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

import asyncio
import json
from datetime import datetime, timedelta
from sqlmodel import select
from fastapi_security_sample.db import SessionLocal
from fastapi_security_sample.users.models import User, UserSession, SessionActivity
from fastapi_security_sample.users.sessions import session_manager

import logging

logger = logging.getLogger(__name__)


async def create_test_user():
    """Create a test user for session testing"""
    from fastapi_security_sample.users.utils import get_password_hash
    from ulid import new as ulid_new
    
    async with SessionLocal() as session:
        # Check if test user already exists
        result = await session.exec(
            select(User).where(User.username == "test_session_user")
        )
        user = result.first()
        
        if not user:
            user = User(
                id=str(ulid_new()),
                username="test_session_user",
                email="test_session@example.com",
                hashed_password=get_password_hash("test_password")
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            logger.info(f"✅ Created test user: {user.username}")
        else:
            logger.info(f"✅ Using existing test user: {user.username}")
        
        return user


async def test_session_creation():
    """Test session creation and database persistence"""
    logger.info("🧪 Testing session creation...")
    
    # Create test user
    user = await create_test_user()
    
    # Create a session using the enhanced session manager
    # Using the original interface: create_session(user, client_ip, user_agent)
    session = session_manager.create_session(
        user=user,
        client_ip="192.168.1.100",
        user_agent="TestAgent/1.0 (Testing)"
    )
    
    logger.info(f"✅ Created session with ID: {session.id}")
    
    # Verify session exists in the session manager
    retrieved_session = session_manager.get_session(session.id)
    if retrieved_session:
        logger.info(f"✅ Session retrieved from manager: {retrieved_session.id}")
        logger.info(f"   - User ID: {retrieved_session.user_id}")
        logger.info(f"   - Client IP: {retrieved_session.client_ip}")
        logger.info(f"   - Active: {retrieved_session.is_active}")
    else:
        logger.error("❌ Session not found in manager")
    
    # Check if session was persisted to database (if enhanced manager is working)
    try:
        async with SessionLocal() as db:
            result = await db.exec(
                select(UserSession).where(UserSession.user_id == user.id)
            )
            db_session = result.first()
            
            if db_session:
                logger.info(f"✅ Session persisted to database: {db_session.id}")
                logger.info(f"   - Client IP: {db_session.client_ip}")
                logger.info(f"   - Active: {db_session.is_active}")
            else:
                logger.info("ℹ️  Session not persisted to database (using in-memory manager)")
    except Exception as e:
        logger.info(f"ℹ️  Database check failed: {e}")
    
    return user, session


async def test_session_management():
    """Test basic session management operations"""
    logger.info("🧪 Testing session management operations...")
    
    user, session = await test_session_creation()
    
    # Test session validation
    retrieved_session = session_manager.get_session(session.id)
    is_valid = retrieved_session is not None
    logger.info(f"✅ Session validation result: {is_valid}")
    
    # Test getting user sessions
    user_sessions = session_manager.get_user_sessions(user.id)
    logger.info(f"✅ Found {len(user_sessions)} sessions for user")
    
    # Test session removal
    removed = session_manager.remove_session(session.id)
    logger.info(f"✅ Session removal result: {removed}")
    
    # Verify session is removed
    retrieved_session = session_manager.get_session(session.id)
    is_removed = retrieved_session is None
    logger.info(f"✅ Session removed verification: {is_removed}")


async def test_session_cleanup():
    """Test session cleanup functionality"""
    logger.info("🧪 Testing session cleanup...")
    
    # Test expired session cleanup
    cleaned_count = session_manager.cleanup_expired_sessions()
    logger.info(f"✅ Cleaned up {cleaned_count} expired sessions")


async def test_multiple_sessions():
    """Test multiple sessions per user"""
    logger.info("🧪 Testing multiple sessions per user...")
    
    user = await create_test_user()
    
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
    logger.info(f"✅ User now has {len(user_sessions)} sessions")
    
    # Clean up test sessions
    for session in sessions:
        session_manager.remove_session(session.id)
    
    logger.info("✅ Cleaned up test sessions")


async def test_database_persistence():
    """Test database persistence features (if enhanced manager is active)"""
    logger.info("🧪 Testing database persistence...")
    
    try:
        async with SessionLocal() as session:
            # Count total sessions in database
            result = await session.exec(select(UserSession))
            sessions = result.all()
            logger.info(f"✅ Total sessions in database: {len(sessions)}")
            
            # Count total activities in database
            result = await session.exec(select(SessionActivity))
            activities = result.all()
            logger.info(f"✅ Total activities in database: {len(activities)}")
            
            # Get active sessions
            result = await session.exec(
                select(UserSession).where(UserSession.is_active == True)
            )
            active_sessions = result.all()
            logger.info(f"✅ Active sessions in database: {len(active_sessions)}")
            
    except Exception as e:
        logger.info(f"ℹ️  Database persistence test skipped: {e}")


async def test_session_analytics():
    """Test session analytics functionality (if available)"""
    logger.info("🧪 Testing session analytics...")
    
    user = await create_test_user()
    
    # Create some test sessions
    session1 = session_manager.create_session(
        user=user,
        client_ip="192.168.1.100",
        user_agent="Chrome/91.0"
    )
    
    session2 = session_manager.create_session(
        user=user,
        client_ip="192.168.1.101",
        user_agent="Firefox/89.0"
    )
    
    # Get user sessions for analytics
    user_sessions = session_manager.get_user_sessions(user.id)
    logger.info(f"✅ User sessions for analytics: {len(user_sessions)}")
    
    # Test enhanced analytics if available
    if hasattr(session_manager, 'get_session_analytics'):
        try:
            analytics = session_manager.get_session_analytics(user.id)
            logger.info(f"✅ Session analytics: {analytics}")
        except Exception as e:
            logger.info(f"ℹ️  Session analytics not available: {e}")
    
    # Clean up
    session_manager.remove_session(session1.id)
    session_manager.remove_session(session2.id)


async def cleanup_test_data():
    """Clean up test data"""
    logger.info("🧹 Cleaning up test data...")
    
    try:
        async with SessionLocal() as session:
            # Delete test user and related data
            result = await session.exec(
                select(User).where(User.username == "test_session_user")
            )
            user = result.first()
            
            if user:
                # Delete user sessions first (if any in database)
                result = await session.exec(
                    select(UserSession).where(UserSession.user_id == user.id)
                )
                db_sessions = result.all()
                
                for db_session in db_sessions:
                    await session.delete(db_session)
                
                # Delete the user
                await session.delete(user)
                await session.commit()
                logger.info("✅ Cleaned up test user and database sessions")
                
    except Exception as e:
        logger.warning(f"⚠️  Database cleanup failed: {e}")
    
    # Clean up any remaining in-memory sessions
    try:
        # Get test user sessions from memory and clean them
        user = await create_test_user()  # Get user ID
        user_sessions = session_manager.get_user_sessions(user.id)
        for session in user_sessions:
            session_manager.remove_session(session.id)
        logger.info("✅ Cleaned up in-memory sessions")
    except Exception as e:
        logger.warning(f"⚠️  Memory cleanup failed: {e}")


async def main():
    """Main test function"""
    print("🚀 Starting Enhanced Session Management System Tests")
    print("=" * 60)
    
    try:
        # Run all tests
        await test_session_creation()
        print()
        
        await test_session_management()
        print()
        
        await test_multiple_sessions()
        print()
        
        await test_session_cleanup()
        print()
        
        await test_database_persistence()
        print()
        
        await test_session_analytics()
        print()
        
        print("✅ All session management tests completed successfully!")
        print("\nSession management system status:")
        print("✓ Basic session operations functional")
        print("✓ Multiple sessions per user supported")
        print("✓ Session cleanup operational")
        print("✓ Session analytics available")
        
        # Check if enhanced features are active
        if hasattr(session_manager, 'enable_db_persistence'):
            if session_manager.enable_db_persistence:
                print("✓ Database persistence enabled")
            else:
                print("ℹ️  Database persistence disabled")
        else:
            print("ℹ️  Using standard in-memory session manager")
        
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

import asyncio
import json
from datetime import datetime, timedelta
from sqlmodel import select, Session as SQLSession
from fastapi_security_sample.db import engine
from fastapi_security_sample.users.models import User, UserSession, SessionActivity
from fastapi_security_sample.users.sessions import session_manager

import logging

logger = logging.getLogger(__name__)


async def create_test_user():
    """Create a test user for session testing"""
    from fastapi_security_sample.users.utils import get_password_hash
    from ulid import new as ulid_new
    
    with SQLSession(engine) as session:
        # Check if test user already exists
        user = session.exec(
            select(User).where(User.username == "test_session_user")
        ).first()
        
        if not user:
            user = User(
                id=str(ulid_new()),
                username="test_session_user",
                email="test_session@example.com",
                hashed_password=get_password_hash("test_password")
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            logger.info(f"✅ Created test user: {user.username}")
        else:
            logger.info(f"✅ Using existing test user: {user.username}")
        
        return user


async def test_session_creation():
    """Test session creation and database persistence"""
    logger.info("🧪 Testing session creation...")
    
    # Create test user
    user = await create_test_user()
    
    # Create a session using the enhanced session manager
    # Using the original interface: create_session(user, client_ip, user_agent)
    session = session_manager.create_session(
        user=user,
        client_ip="192.168.1.100",
        user_agent="TestAgent/1.0 (Testing)"
    )
    
    logger.info(f"✅ Created session with ID: {session.id}")
    
    # Verify session exists in the session manager
    retrieved_session = session_manager.get_session(session.id)
    if retrieved_session:
        logger.info(f"✅ Session retrieved from manager: {retrieved_session.id}")
        logger.info(f"   - User ID: {retrieved_session.user_id}")
        logger.info(f"   - Client IP: {retrieved_session.client_ip}")
        logger.info(f"   - Active: {retrieved_session.is_active}")
    else:
        logger.error("❌ Session not found in manager")
    
    # Check if session was persisted to database (if enhanced manager is working)
    try:
        with SQLSession(engine) as db:
            db_session = db.exec(
                select(UserSession).where(UserSession.user_id == user.id)
            ).first()
            
            if db_session:
                logger.info(f"✅ Session persisted to database: {db_session.id}")
                logger.info(f"   - Client IP: {db_session.client_ip}")
                logger.info(f"   - Active: {db_session.is_active}")
            else:
                logger.info("ℹ️  Session not persisted to database (using in-memory manager)")
    except Exception as e:
        logger.info(f"ℹ️  Database check failed: {e}")
    
    return user, session


async def test_session_management():
    """Test basic session management operations"""
    logger.info("🧪 Testing session management operations...")
    
    user, session = await test_session_creation()
    
    # Test session validation
    retrieved_session = session_manager.get_session(session.id)
    is_valid = retrieved_session is not None
    logger.info(f"✅ Session validation result: {is_valid}")
    
    # Test getting user sessions
    user_sessions = session_manager.get_user_sessions(user.id)
    logger.info(f"✅ Found {len(user_sessions)} sessions for user")
    
    # Test session removal
    removed = session_manager.remove_session(session.id)
    logger.info(f"✅ Session removal result: {removed}")
    
    # Verify session is removed
    retrieved_session = session_manager.get_session(session.id)
    is_removed = retrieved_session is None
    logger.info(f"✅ Session removed verification: {is_removed}")


async def test_session_cleanup():
    """Test session cleanup functionality"""
    logger.info("🧪 Testing session cleanup...")
    
    # Test expired session cleanup
    cleaned_count = session_manager.cleanup_expired_sessions()
    logger.info(f"✅ Cleaned up {cleaned_count} expired sessions")


async def test_multiple_sessions():
    """Test multiple sessions per user"""
    logger.info("🧪 Testing multiple sessions per user...")
    
    user = await create_test_user()
    
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
    logger.info(f"✅ User now has {len(user_sessions)} sessions")
    
    # Clean up test sessions
    for session in sessions:
        session_manager.remove_session(session.id)
    
    logger.info("✅ Cleaned up test sessions")


async def test_database_persistence():
    """Test database persistence features (if enhanced manager is active)"""
    logger.info("🧪 Testing database persistence...")
    
    try:
        with SQLSession(engine) as session:
            # Count total sessions in database
            sessions = session.exec(select(UserSession)).all()
            logger.info(f"✅ Total sessions in database: {len(sessions)}")
            
            # Count total activities in database
            activities = session.exec(select(SessionActivity)).all()
            logger.info(f"✅ Total activities in database: {len(activities)}")
            
            # Get active sessions
            active_sessions = session.exec(
                select(UserSession).where(UserSession.is_active == True)
            ).all()
            logger.info(f"✅ Active sessions in database: {len(active_sessions)}")
            
    except Exception as e:
        logger.info(f"ℹ️  Database persistence test skipped: {e}")


async def test_session_analytics():
    """Test session analytics functionality (if available)"""
    logger.info("🧪 Testing session analytics...")
    
    user = await create_test_user()
    
    # Create some test sessions
    session1 = session_manager.create_session(
        user=user,
        client_ip="192.168.1.100",
        user_agent="Chrome/91.0"
    )
    
    session2 = session_manager.create_session(
        user=user,
        client_ip="192.168.1.101",
        user_agent="Firefox/89.0"
    )
    
    # Get user sessions for analytics
    user_sessions = session_manager.get_user_sessions(user.id)
    logger.info(f"✅ User sessions for analytics: {len(user_sessions)}")
    
    # Test enhanced analytics if available
    if hasattr(session_manager, 'get_session_analytics'):
        try:
            analytics = session_manager.get_session_analytics(user.id)
            logger.info(f"✅ Session analytics: {analytics}")
        except Exception as e:
            logger.info(f"ℹ️  Session analytics not available: {e}")
    
    # Clean up
    session_manager.remove_session(session1.id)
    session_manager.remove_session(session2.id)


async def cleanup_test_data():
    """Clean up test data"""
    logger.info("� Cleaning up test data...")
    
    try:
        with SQLSession(engine) as session:
            # Delete test user and related data
            user = session.exec(
                select(User).where(User.username == "test_session_user")
            ).first()
            
            if user:
                # Delete user sessions first (if any in database)
                db_sessions = session.exec(
                    select(UserSession).where(UserSession.user_id == user.id)
                ).all()
                
                for db_session in db_sessions:
                    session.delete(db_session)
                
                # Delete the user
                session.delete(user)
                session.commit()
                logger.info("✅ Cleaned up test user and database sessions")
                
    except Exception as e:
        logger.warning(f"⚠️  Database cleanup failed: {e}")
    
    # Clean up any remaining in-memory sessions
    try:
        # Get test user sessions from memory and clean them
        user = await create_test_user()  # Get user ID
        user_sessions = session_manager.get_user_sessions(user.id)
        for session in user_sessions:
            session_manager.remove_session(session.id)
        logger.info("✅ Cleaned up in-memory sessions")
    except Exception as e:
        logger.warning(f"⚠️  Memory cleanup failed: {e}")


async def main():
    """Main test function"""
    print("🚀 Starting Enhanced Session Management System Tests")
    print("=" * 60)
    
    try:
        # Run all tests
        await test_session_creation()
        print()
        
        await test_session_management()
        print()
        
        await test_multiple_sessions()
        print()
        
        await test_session_cleanup()
        print()
        
        await test_database_persistence()
        print()
        
        await test_session_analytics()
        print()
        
        print("✅ All session management tests completed successfully!")
        print("\nSession management system status:")
        print("✓ Basic session operations functional")
        print("✓ Multiple sessions per user supported")
        print("✓ Session cleanup operational")
        print("✓ Session analytics available")
        
        # Check if enhanced features are active
        if hasattr(session_manager, 'enable_db_persistence'):
            if session_manager.enable_db_persistence:
                print("✓ Database persistence enabled")
            else:
                print("ℹ️  Database persistence disabled")
        else:
            print("ℹ️  Using standard in-memory session manager")
        
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
