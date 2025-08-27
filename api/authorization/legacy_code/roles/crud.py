from typing import Optional, List
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from sqlalchemy.exc import IntegrityError
from ..models import Role, Permission, RolePermission, User
from datetime import datetime


# Role CRUD operations
async def create_role(db: AsyncSession, role_id: str, name: str, description: Optional[str] = None) -> Role:
    """Create a new role"""
    role = Role(
        id=role_id,
        name=name,
        description=description
    )
    db.add(role)
    try:
        await db.commit()
        await db.refresh(role)
        return role
    except IntegrityError:
        await db.rollback()
        raise


async def get_role_by_id(db: AsyncSession, role_id: str) -> Optional[Role]:
    """Get role by ID"""
    statement = select(Role).where(Role.id == role_id)
    result = await db.execute(statement)
    return result.scalar_one_or_none()


async def get_role_by_name(db: AsyncSession, name: str) -> Optional[Role]:
    """Get role by name"""
    statement = select(Role).where(Role.name == name)
    result = await db.execute(statement)
    return result.scalar_one_or_none()


async def list_roles(db: AsyncSession) -> List[Role]:
    """List all roles"""
    statement = select(Role)
    result = await db.execute(statement)
    return list(result.scalars().all())


async def update_role(db: AsyncSession, role_id: str, updates: dict) -> Optional[Role]:
    """Update a role"""
    role = await get_role_by_id(db, role_id)
    if not role:
        return None
    
    for key, value in updates.items():
        if hasattr(role, key):
            setattr(role, key, value)
    
    role.updated_at = datetime.utcnow()
    
    try:
        await db.commit()
        await db.refresh(role)
        return role
    except IntegrityError:
        await db.rollback()
        raise


async def delete_role(db: AsyncSession, role_id: str) -> bool:
    """Delete a role"""
    role = await get_role_by_id(db, role_id)
    if not role:
        return False
    
    await db.delete(role)
    await db.commit()
    return True


# Permission CRUD operations
async def create_permission(db: AsyncSession, permission_id: str, name: str, resource: str, action: str, description: Optional[str] = None) -> Permission:
    """Create a new permission"""
    permission = Permission(
        id=permission_id,
        name=name,
        resource=resource,
        action=action,
        description=description
    )
    db.add(permission)
    try:
        await db.commit()
        await db.refresh(permission)
        return permission
    except IntegrityError:
        await db.rollback()
        raise


async def get_permission_by_id(db: AsyncSession, permission_id: str) -> Optional[Permission]:
    """Get permission by ID"""
    statement = select(Permission).where(Permission.id == permission_id)
    result = await db.execute(statement)
    return result.scalar_one_or_none()


async def get_permission_by_name(db: AsyncSession, name: str) -> Optional[Permission]:
    """Get permission by name"""
    statement = select(Permission).where(Permission.name == name)
    result = await db.execute(statement)
    return result.scalar_one_or_none()


async def list_permissions(db: AsyncSession) -> List[Permission]:
    """List all permissions"""
    statement = select(Permission)
    result = await db.execute(statement)
    return list(result.scalars().all())


async def get_permissions_by_resource(db: AsyncSession, resource: str) -> List[Permission]:
    """Get all permissions for a resource"""
    statement = select(Permission).where(Permission.resource == resource)
    result = await db.execute(statement)
    return list(result.scalars().all())


# Role-Permission associations
async def assign_permission_to_role(db: AsyncSession, role_id: str, permission_id: str) -> bool:
    """Assign a permission to a role"""
    # Check if role and permission exist
    role = await get_role_by_id(db, role_id)
    permission = await get_permission_by_id(db, permission_id)
    
    if not role or not permission:
        return False
    
    # Check if association already exists
    statement = select(RolePermission).where(
        RolePermission.role_id == role_id,
        RolePermission.permission_id == permission_id
    )
    result = await db.execute(statement)
    existing = result.scalar_one_or_none()
    
    if existing:
        return True  # Already assigned
    
    # Create association
    role_permission = RolePermission(role_id=role_id, permission_id=permission_id)
    db.add(role_permission)
    await db.commit()
    return True


async def remove_permission_from_role(db: AsyncSession, role_id: str, permission_id: str) -> bool:
    """Remove a permission from a role"""
    statement = select(RolePermission).where(
        RolePermission.role_id == role_id,
        RolePermission.permission_id == permission_id
    )
    result = await db.execute(statement)
    role_permission = result.scalar_one_or_none()
    
    if not role_permission:
        return False
    
    await db.delete(role_permission)
    await db.commit()
    return True


async def get_role_permissions(db: AsyncSession, role_id: str) -> List[Permission]:
    """Get all permissions for a role"""
    statement = (
        select(Permission)
        .join(RolePermission)
        .where(RolePermission.role_id == role_id, RolePermission.permission_id == Permission.id)
    )
    result = await db.execute(statement)
    return list(result.scalars().all())


async def get_user_permissions(db: AsyncSession, user_id: str) -> List[Permission]:
    """Get all permissions for a user through their role"""
    statement = (
        select(Permission)
        .join(RolePermission)
        .join(Role)
        .join(User)
        .where(
            User.id == user_id,
            User.is_deleted == False,
            User.role_id == Role.id,
            Role.id == RolePermission.role_id,
            RolePermission.permission_id == Permission.id
        )
    )
    result = await db.execute(statement)
    return list(result.scalars().all())


async def user_has_permission(db: AsyncSession, user_id: str, resource: str, action: str) -> bool:
    """Check if user has a specific permission"""
    statement = (
        select(Permission)
        .join(RolePermission)
        .join(Role)
        .join(User)
        .where(
            User.id == user_id,
            User.is_deleted == False,
            Permission.resource == resource,
            Permission.action == action,
            User.role_id == Role.id,
            Role.id == RolePermission.role_id,
            RolePermission.permission_id == Permission.id
        )
    )
    result = await db.execute(statement)
    permission = result.scalar_one_or_none()
    return permission is not None
