"""
Groups CRUD operations.

This module provides database operations for groups and group memberships,
including creating, reading, updating, and deleting groups and managing memberships.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.orm import selectinload
from datetime import datetime
import json
import re

from api.groups.models import Group, UserGroup
from api.groups.schemas import GroupCreate, GroupUpdate, GroupMembershipRequest, GroupMembershipUpdate
from api.users.models import User
from api.common.exceptions import NotFoundError, ValidationError, ConflictError
from api.common.utils import generate_id, create_slug


class GroupCRUD:
    """CRUD operations for groups."""
    
    async def create_group(
        self, 
        db: AsyncSession, 
        group_data: GroupCreate, 
        owner_id: str,
        created_by: str
    ) -> Group:
        """Create a new group."""
        # Generate slug from name
        slug = create_slug(group_data.name)
        
        # Check if group name or slug already exists
        existing = await db.execute(
            select(Group).where(
                or_(
                    Group.name == group_data.name,
                    Group.slug == slug
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ConflictError("Group with this name already exists")
        
        # Create group
        group = Group(
            id=generate_id(),
            slug=slug,
            owner_id=owner_id,
            created_by=created_by,
            **group_data.dict()
        )
        
        db.add(group)
        await db.commit()
        await db.refresh(group)
        
        # Add owner as admin member
        await self.add_user_to_group(
            db=db,
            group_id=group.id,
            user_id=owner_id,
            role_in_group="admin",
            added_by=created_by
        )
        
        return group
    
    async def get_group(
        self, 
        db: AsyncSession, 
        group_id: str,
        include_members: bool = False
    ) -> Optional[Group]:
        """Get a group by ID."""
        query = select(Group).where(
            and_(Group.id == group_id, Group.deleted_at.is_(None))
        )
        
        if include_members:
            query = query.options(selectinload(Group.members))
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_group_by_slug(
        self, 
        db: AsyncSession, 
        slug: str,
        include_members: bool = False
    ) -> Optional[Group]:
        """Get a group by slug."""
        query = select(Group).where(
            and_(Group.slug == slug, Group.deleted_at.is_(None))
        )
        
        if include_members:
            query = query.options(selectinload(Group.members))
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_groups(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        group_type: Optional[str] = None,
        is_public: Optional[bool] = None,
        is_active: Optional[bool] = True,
        owner_id: Optional[str] = None,
        order_by: str = "created_at",
        order_direction: str = "desc"
    ) -> tuple[List[Group], int]:
        """Get groups with filtering and pagination."""
        # Base query
        query = select(Group).where(Group.deleted_at.is_(None))
        count_query = select(func.count(Group.id)).where(Group.deleted_at.is_(None))
        
        # Apply filters
        if search:
            search_filter = or_(
                Group.name.ilike(f"%{search}%"),
                Group.description.ilike(f"%{search}%"),
                Group.tags.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)
        
        if group_type:
            query = query.where(Group.group_type == group_type)
            count_query = count_query.where(Group.group_type == group_type)
        
        if is_public is not None:
            query = query.where(Group.is_public == is_public)
            count_query = count_query.where(Group.is_public == is_public)
        
        if is_active is not None:
            query = query.where(Group.is_active == is_active)
            count_query = count_query.where(Group.is_active == is_active)
        
        if owner_id:
            query = query.where(Group.owner_id == owner_id)
            count_query = count_query.where(Group.owner_id == owner_id)
        
        # Apply ordering
        order_column = getattr(Group, order_by, Group.created_at)
        if order_direction.lower() == "desc":
            query = query.order_by(desc(order_column))
        else:
            query = query.order_by(asc(order_column))
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute queries
        result = await db.execute(query)
        groups = result.scalars().all()
        
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        return list(groups), total
    
    async def update_group(
        self,
        db: AsyncSession,
        group_id: str,
        group_data: GroupUpdate,
        updated_by: str
    ) -> Optional[Group]:
        """Update a group."""
        group = await self.get_group(db, group_id)
        if not group:
            raise NotFoundError("Group not found")
        
        # Check if new name conflicts
        update_data = group_data.dict(exclude_unset=True)
        if "name" in update_data and update_data["name"] != group.name:
            slug = create_slug(update_data["name"])
            existing = await db.execute(
                select(Group).where(
                    and_(
                        or_(Group.name == update_data["name"], Group.slug == slug),
                        Group.id != group_id
                    )
                )
            )
            if existing.scalar_one_or_none():
                raise ConflictError("Group with this name already exists")
            
            update_data["slug"] = slug
        
        # Update fields
        for field, value in update_data.items():
            setattr(group, field, value)
        
        group.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(group)
        
        return group
    
    async def delete_group(
        self,
        db: AsyncSession,
        group_id: str,
        deleted_by: str
    ) -> bool:
        """Soft delete a group."""
        group = await self.get_group(db, group_id)
        if not group:
            raise NotFoundError("Group not found")
        
        if group.is_system:
            raise ValidationError("Cannot delete system groups")
        
        group.deleted_at = datetime.utcnow()
        group.is_active = False
        
        await db.commit()
        return True
    
    async def add_user_to_group(
        self,
        db: AsyncSession,
        group_id: str,
        user_id: str,
        role_in_group: str = "member",
        added_by: Optional[str] = None
    ) -> UserGroup:
        """Add a user to a group."""
        # Check if group exists
        group = await self.get_group(db, group_id)
        if not group:
            raise NotFoundError("Group not found")
        
        # Check if user exists
        user_result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        if not user:
            raise NotFoundError("User not found")
        
        # Check if membership already exists
        existing = await db.execute(
            select(UserGroup).where(
                and_(
                    UserGroup.user_id == user_id,
                    UserGroup.group_id == group_id
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ConflictError("User is already a member of this group")
        
        # Check group capacity
        if group.max_members and group.member_count >= group.max_members:
            raise ValidationError("Group has reached maximum capacity")
        
        # Create membership
        membership = UserGroup(
            user_id=user_id,
            group_id=group_id,
            role_in_group=role_in_group,
            joined_by=added_by
        )
        
        db.add(membership)
        
        # Update member count
        group.member_count += 1
        
        await db.commit()
        await db.refresh(membership)
        
        return membership
    
    async def remove_user_from_group(
        self,
        db: AsyncSession,
        group_id: str,
        user_id: str
    ) -> bool:
        """Remove a user from a group."""
        # Get membership
        result = await db.execute(
            select(UserGroup).where(
                and_(
                    UserGroup.user_id == user_id,
                    UserGroup.group_id == group_id
                )
            )
        )
        membership = result.scalar_one_or_none()
        
        if not membership:
            raise NotFoundError("User is not a member of this group")
        
        # Remove membership
        await db.delete(membership)
        
        # Update member count
        group = await self.get_group(db, group_id)
        if group:
            group.member_count = max(0, group.member_count - 1)
        
        await db.commit()
        return True
    
    async def update_user_group_membership(
        self,
        db: AsyncSession,
        group_id: str,
        user_id: str,
        membership_data: GroupMembershipUpdate
    ) -> Optional[UserGroup]:
        """Update a user's group membership."""
        # Get membership
        result = await db.execute(
            select(UserGroup).where(
                and_(
                    UserGroup.user_id == user_id,
                    UserGroup.group_id == group_id
                )
            )
        )
        membership = result.scalar_one_or_none()
        
        if not membership:
            raise NotFoundError("User is not a member of this group")
        
        # Update fields
        update_data = membership_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(membership, field, value)
        
        await db.commit()
        await db.refresh(membership)
        
        return membership
    
    async def get_group_members(
        self,
        db: AsyncSession,
        group_id: str,
        skip: int = 0,
        limit: int = 100,
        role_filter: Optional[str] = None,
        active_only: bool = True
    ) -> tuple[List[tuple[User, UserGroup]], int]:
        """Get group members with their membership info."""
        # Base query
        query = (
            select(User, UserGroup)
            .join(UserGroup, User.id == UserGroup.user_id)
            .where(UserGroup.group_id == group_id)
        )
        
        count_query = (
            select(func.count(UserGroup.user_id))
            .where(UserGroup.group_id == group_id)
        )
        
        # Apply filters
        if role_filter:
            query = query.where(UserGroup.role_in_group == role_filter)
            count_query = count_query.where(UserGroup.role_in_group == role_filter)
        
        if active_only:
            query = query.where(
                and_(
                    UserGroup.is_active == True,
                    User.is_active == True
                )
            )
            count_query = count_query.where(
                and_(
                    UserGroup.is_active == True,
                    User.is_active == True
                )
            )
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute queries
        result = await db.execute(query)
        members = result.all()
        
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        return list(members), total
    
    async def get_user_groups(
        self,
        db: AsyncSession,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = True
    ) -> tuple[List[tuple[Group, UserGroup]], int]:
        """Get groups that a user is a member of."""
        # Base query
        query = (
            select(Group, UserGroup)
            .join(UserGroup, Group.id == UserGroup.group_id)
            .where(
                and_(
                    UserGroup.user_id == user_id,
                    Group.deleted_at.is_(None)
                )
            )
        )
        
        count_query = (
            select(func.count(UserGroup.group_id))
            .join(Group, Group.id == UserGroup.group_id)
            .where(
                and_(
                    UserGroup.user_id == user_id,
                    Group.deleted_at.is_(None)
                )
            )
        )
        
        # Apply filters
        if active_only:
            query = query.where(
                and_(
                    UserGroup.is_active == True,
                    Group.is_active == True
                )
            )
            count_query = count_query.where(
                and_(
                    UserGroup.is_active == True,
                    Group.is_active == True
                )
            )
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        # Execute queries
        result = await db.execute(query)
        groups = result.all()
        
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        return list(groups), total


# Create singleton instance
group_crud = GroupCRUD()
