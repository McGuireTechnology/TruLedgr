"""
Role and Permission service layer.
"""
from typing import Optional, List
from sqlmodel.ext.asyncio.session import AsyncSession
from ..models import Role, Permission
from . import crud


# Role service functions
async def create_role(db: AsyncSession, role_id: str, name: str, description: Optional[str] = None) -> Role:
    """Create a new role"""
    return await crud.create_role(db, role_id, name, description)


async def get_role_by_id(db: AsyncSession, role_id: str) -> Optional[Role]:
    """Get role by ID"""
    return await crud.get_role_by_id(db, role_id)


async def get_role_by_name(db: AsyncSession, name: str) -> Optional[Role]:
    """Get role by name"""
    return await crud.get_role_by_name(db, name)


async def list_roles(db: AsyncSession) -> List[Role]:
    """List all roles"""
    return await crud.list_roles(db)


async def update_role(db: AsyncSession, role_id: str, updates: dict) -> Optional[Role]:
    """Update a role"""
    return await crud.update_role(db, role_id, updates)


async def delete_role(db: AsyncSession, role_id: str) -> bool:
    """Delete a role"""
    return await crud.delete_role(db, role_id)


# Permission service functions
async def create_permission(db: AsyncSession, permission_id: str, name: str, resource: str, action: str, description: Optional[str] = None) -> Permission:
    """Create a new permission"""
    return await crud.create_permission(db, permission_id, name, resource, action, description)


async def get_permission_by_id(db: AsyncSession, permission_id: str) -> Optional[Permission]:
    """Get permission by ID"""
    return await crud.get_permission_by_id(db, permission_id)


async def get_permission_by_name(db: AsyncSession, name: str) -> Optional[Permission]:
    """Get permission by name"""
    return await crud.get_permission_by_name(db, name)


async def list_permissions(db: AsyncSession) -> List[Permission]:
    """List all permissions"""
    return await crud.list_permissions(db)


async def get_permissions_by_resource(db: AsyncSession, resource: str) -> List[Permission]:
    """Get all permissions for a resource"""
    return await crud.get_permissions_by_resource(db, resource)


# Role-Permission association functions
async def assign_permission_to_role(db: AsyncSession, role_id: str, permission_id: str) -> bool:
    """Assign a permission to a role"""
    return await crud.assign_permission_to_role(db, role_id, permission_id)


async def remove_permission_from_role(db: AsyncSession, role_id: str, permission_id: str) -> bool:
    """Remove a permission from a role"""
    return await crud.remove_permission_from_role(db, role_id, permission_id)


async def get_role_permissions(db: AsyncSession, role_id: str) -> List[Permission]:
    """Get all permissions for a role"""
    return await crud.get_role_permissions(db, role_id)


async def get_user_permissions(db: AsyncSession, user_id: str) -> List[Permission]:
    """Get all permissions for a user through their role"""
    return await crud.get_user_permissions(db, user_id)


async def user_has_permission(db: AsyncSession, user_id: str, resource: str, action: str) -> bool:
    """Check if user has a specific permission"""
    return await crud.user_has_permission(db, user_id, resource, action)
