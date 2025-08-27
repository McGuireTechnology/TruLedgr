"""
Authorization service layer for RBAC operations.

This module provides business logic for role and permission management
including user role assignments, permission checks, and RBAC queries.
"""

from typing import List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from ulid import new as ulid_new

from .models import Role, Permission, RolePermission
from api.authorization.utils.scopes import Scopes


async def get_role_by_id(session: AsyncSession, role_id: str) -> Optional[Role]:
    """Get role by ID."""
    statement = select(Role).where(Role.id == role_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def get_role_by_name(session: AsyncSession, name: str) -> Optional[Role]:
    """Get role by name."""
    statement = select(Role).where(Role.name == name)
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def create_role(
    session: AsyncSession, 
    role_id: str, 
    name: str, 
    description: Optional[str] = None,
    is_system: bool = False
) -> Role:
    """Create a new role."""
    role = Role(
        id=role_id,
        name=name,
        description=description,
        is_system=is_system
    )
    session.add(role)
    await session.commit()
    await session.refresh(role)
    return role


async def update_role(
    session: AsyncSession,
    role_id: str,
    updates: dict
) -> Optional[Role]:
    """Update role information."""
    role = await get_role_by_id(session, role_id)
    if not role:
        return None
    
    for key, value in updates.items():
        if hasattr(role, key):
            setattr(role, key, value)
    
    await session.commit()
    await session.refresh(role)
    return role


async def delete_role(session: AsyncSession, role_id: str) -> bool:
    """Delete a role (only if not system role)."""
    role = await get_role_by_id(session, role_id)
    if not role or role.is_system:
        return False
    
    await session.delete(role)
    await session.commit()
    return True


async def list_roles(session: AsyncSession, include_inactive: bool = False) -> List[Role]:
    """List all roles."""
    statement = select(Role)
    if not include_inactive:
        statement = statement.where(Role.is_active == True)
    
    result = await session.execute(statement)
    return list(result.scalars().all())


# Permission management
async def get_permission_by_id(session: AsyncSession, permission_id: str) -> Optional[Permission]:
    """Get permission by ID."""
    statement = select(Permission).where(Permission.id == permission_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def get_permission_by_name(session: AsyncSession, name: str) -> Optional[Permission]:
    """Get permission by name."""
    statement = select(Permission).where(Permission.name == name)
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def create_permission(
    session: AsyncSession,
    permission_id: str,
    name: str,
    description: Optional[str] = None,
    resource: str = "",
    action: str = "",
    is_system: bool = False
) -> Permission:
    """Create a new permission."""
    permission = Permission(
        id=permission_id,
        name=name,
        description=description,
        resource=resource,
        action=action,
        is_system=is_system
    )
    session.add(permission)
    await session.commit()
    await session.refresh(permission)
    return permission


async def list_permissions(session: AsyncSession) -> List[Permission]:
    """List all permissions."""
    statement = select(Permission)
    result = await session.execute(statement)
    return list(result.scalars().all())


async def assign_permission_to_role(
    session: AsyncSession,
    role_id: str,
    permission_id: str,
    assigned_by: Optional[str] = None
) -> bool:
    """Assign a permission to a role."""
    # Check if assignment already exists
    statement = select(RolePermission).where(
        RolePermission.role_id == role_id,
        RolePermission.permission_id == permission_id
    )
    result = await session.execute(statement)
    if result.scalar_one_or_none():
        return False  # Already assigned
    
    role_permission = RolePermission(
        role_id=role_id,
        permission_id=permission_id,
        assigned_by=assigned_by
    )
    session.add(role_permission)
    await session.commit()
    return True


async def remove_permission_from_role(
    session: AsyncSession,
    role_id: str,
    permission_id: str
) -> bool:
    """Remove a permission from a role."""
    statement = select(RolePermission).where(
        RolePermission.role_id == role_id,
        RolePermission.permission_id == permission_id
    )
    result = await session.execute(statement)
    role_permission = result.scalar_one_or_none()
    
    if not role_permission:
        return False
    
    await session.delete(role_permission)
    await session.commit()
    return True


async def get_role_permissions(session: AsyncSession, role_id: str) -> List[Permission]:
    """Get all permissions for a role."""
    statement = (
        select(Permission)
        .join(RolePermission)
        .where(RolePermission.role_id == role_id)
    )
    result = await session.execute(statement)
    return list(result.scalars().all())


# User permission checks
async def get_user_permissions(session: AsyncSession, user_id: str) -> List[str]:
    """Get all permission scopes for a user."""
    # This function would need to be implemented based on your User model
    # For now, return empty list
    from api.users.service import get_user_by_id
    
    user = await get_user_by_id(session, user_id)
    if not user or not user.role_id:
        return []
    
    permissions = await get_role_permissions(session, user.role_id)
    return [perm.name for perm in permissions]


async def check_user_permission(
    session: AsyncSession, 
    user_id: str, 
    required_permission: str
) -> bool:
    """Check if user has a specific permission."""
    user_permissions = await get_user_permissions(session, user_id)
    return required_permission in user_permissions


async def assign_role_to_user(session: AsyncSession, user_id: str, role_id: str) -> bool:
    """Assign a role to a user."""
    from api.users.service import get_user_by_id
    
    user = await get_user_by_id(session, user_id)
    if not user:
        return False
    
    role = await get_role_by_id(session, role_id)
    if not role:
        return False
    
    user.role_id = role_id
    await session.commit()
    return True


async def remove_role_from_user(session: AsyncSession, user_id: str) -> bool:
    """Remove role from a user."""
    from api.users.service import get_user_by_id
    
    user = await get_user_by_id(session, user_id)
    if not user:
        return False
    
    user.role_id = None
    await session.commit()
    return True
