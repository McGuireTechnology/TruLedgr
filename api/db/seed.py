"""
Database seeding utilities for initial data.

This module provides functions to seed the database with:
- Default roles (user, admin, moderator)
- Default permissions for each resource
- Initial admin user (optional)
"""

import asyncio
from sqlmodel.ext.asyncio.session import AsyncSession
from ulid import new as ulid_new

from api.db.session import SessionLocal
from api.settings import get_settings


async def seed_roles(session: AsyncSession):
    """
    Seed default roles in the database.
    
    Args:
        session: Database session
    """
    from api.authorization.models import Role
    from api.authorization.service import get_role_by_name, create_role
    
    default_roles = [
        {
            "id": str(ulid_new()),
            "name": "user",
            "description": "Standard user with basic permissions"
        },
        {
            "id": str(ulid_new()),
            "name": "admin", 
            "description": "Administrator with full system access"
        },
        {
            "id": str(ulid_new()),
            "name": "moderator",
            "description": "Moderator with content management permissions"
        }
    ]
    
    for role_data in default_roles:
        existing_role = await get_role_by_name(session, role_data["name"])
        if not existing_role:
            await create_role(
                session,
                role_data["id"],
                role_data["name"],
                role_data["description"]
            )
            print(f"Created role: {role_data['name']}")


async def seed_permissions(session: AsyncSession):
    """
    Seed default permissions in the database.
    
    Args:
        session: Database session
    """
    from api.authorization.models import Permission
    from api.authorization.service import get_permission_by_name, create_permission
    
    # Define resources and their actions
    resources_actions = {
        "users": ["create", "read", "update", "delete", "list"],
        "groups": ["create", "read", "update", "delete", "list", "manage_members"],
        "roles": ["create", "read", "update", "delete", "list", "assign"],
        "permissions": ["create", "read", "update", "delete", "list", "assign"],
        "sessions": ["read", "revoke", "list"],
        "admin": ["access", "manage", "monitor"]
    }
    
    for resource, actions in resources_actions.items():
        for action in actions:
            permission_name = f"{resource}:{action}"
            existing_permission = await get_permission_by_name(session, permission_name)
            
            if not existing_permission:
                await create_permission(
                    session,
                    str(ulid_new()),
                    permission_name,
                    f"{action.title()} {resource}",
                    resource,
                    action
                )
                print(f"Created permission: {permission_name}")


async def seed_role_permissions(session: AsyncSession):
    """
    Assign default permissions to roles.
    
    Args:
        session: Database session
    """
    from api.authorization.service import (
        get_role_by_name, 
        get_permission_by_name,
        assign_permission_to_role
    )
    
    # Admin gets all permissions
    admin_role = await get_role_by_name(session, "admin")
    if admin_role:
        all_permissions = [
            "users:create", "users:read", "users:update", "users:delete", "users:list",
            "groups:create", "groups:read", "groups:update", "groups:delete", "groups:list", "groups:manage_members",
            "roles:create", "roles:read", "roles:update", "roles:delete", "roles:list", "roles:assign",
            "permissions:create", "permissions:read", "permissions:update", "permissions:delete", "permissions:list", "permissions:assign",
            "sessions:read", "sessions:revoke", "sessions:list",
            "admin:access", "admin:manage", "admin:monitor"
        ]
        
        for perm_name in all_permissions:
            permission = await get_permission_by_name(session, perm_name)
            if permission:
                await assign_permission_to_role(session, admin_role.id, permission.id)
    
    # Moderator gets content management permissions
    moderator_role = await get_role_by_name(session, "moderator")
    if moderator_role:
        moderator_permissions = [
            "users:read", "users:list",
            "groups:create", "groups:read", "groups:update", "groups:list", "groups:manage_members",
            "sessions:read", "sessions:list"
        ]
        
        for perm_name in moderator_permissions:
            permission = await get_permission_by_name(session, perm_name)
            if permission:
                await assign_permission_to_role(session, moderator_role.id, permission.id)
    
    # User gets basic permissions
    user_role = await get_role_by_name(session, "user")
    if user_role:
        user_permissions = [
            "groups:read", "groups:list",
            "sessions:read"
        ]
        
        for perm_name in user_permissions:
            permission = await get_permission_by_name(session, perm_name)
            if permission:
                await assign_permission_to_role(session, user_role.id, permission.id)


async def seed_admin_user(session: AsyncSession, email: str = "admin@example.com", password: str = "admin123"):
    """
    Create initial admin user.
    
    Args:
        session: Database session
        email: Admin user email
        password: Admin user password
    """
    from api.users.service import get_user_by_email, create_user_from_model
    from api.users.models import User
    from api.authorization.service import get_role_by_name
    from api.authentication.utils.password import get_password_hash
    
    # Check if admin user already exists
    existing_admin = await get_user_by_email(session, email)
    if existing_admin:
        print(f"Admin user {email} already exists")
        return
    
    # Get admin role
    admin_role = await get_role_by_name(session, "admin")
    if not admin_role:
        print("Admin role not found. Please seed roles first.")
        return
    
    # Create admin user
    admin_user = User(
        id=str(ulid_new()),
        username="admin",
        email=email,
        hashed_password=get_password_hash(password),
        role_id=admin_role.id,
        email_verified=True
    )
    
    created_user = await create_user_from_model(session, admin_user)
    print(f"Created admin user: {created_user.email}")


async def seed_database():
    """
    Run all seeding operations.
    
    This function should be called during application startup
    or as a separate script for initial database setup.
    """
    async with SessionLocal() as session:
        try:
            print("Starting database seeding...")
            
            # Seed in correct order due to dependencies
            await seed_roles(session)
            await seed_permissions(session)
            await seed_role_permissions(session)
            
            # Optionally create admin user
            settings = get_settings()
            if settings.is_development:
                await seed_admin_user(session)
            
            await session.commit()
            print("Database seeding completed successfully!")
            
        except Exception as e:
            await session.rollback()
            print(f"Error during database seeding: {e}")
            raise


if __name__ == "__main__":
    # Run seeding as a script
    asyncio.run(seed_database())
