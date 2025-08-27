"""
Groups service layer.

This module provides business logic for group operations,
including group management, membership handling, and permissions.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from api.groups.crud import group_crud
from api.groups.schemas import (
    GroupCreate, GroupUpdate, Group, GroupWithMembers, 
    GroupMembershipRequest, GroupMembershipUpdate,
    UserInGroup, GroupStats, GroupListResponse
)
from api.users.models import User
from api.common.exceptions import NotFoundError, ValidationError, ConflictError
from api.common.utils import calculate_pagination


class GroupService:
    """Service class for group operations."""
    
    def __init__(self):
        self.crud = group_crud
    
    async def create_group(
        self,
        db: AsyncSession,
        group_data: GroupCreate,
        current_user: User
    ) -> Group:
        """Create a new group."""
        try:
            group = await self.crud.create_group(
                db=db,
                group_data=group_data,
                owner_id=current_user.id,
                created_by=current_user.id
            )
            return Group.from_orm(group)
        except ConflictError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create group"
            )
    
    async def get_group(
        self,
        db: AsyncSession,
        group_id: str,
        current_user: User,
        include_members: bool = False
    ) -> Group:
        """Get a group by ID."""
        group = await self.crud.get_group(
            db=db,
            group_id=group_id,
            include_members=include_members
        )
        
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found"
            )
        
        # Check visibility permissions
        if not group.is_public and not await self._user_can_view_group(db, current_user.id, group_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        if include_members:
            return GroupWithMembers.from_orm(group)
        return Group.from_orm(group)
    
    async def get_group_by_slug(
        self,
        db: AsyncSession,
        slug: str,
        current_user: User,
        include_members: bool = False
    ) -> Group:
        """Get a group by slug."""
        group = await self.crud.get_group_by_slug(
            db=db,
            slug=slug,
            include_members=include_members
        )
        
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found"
            )
        
        # Check visibility permissions
        if not group.is_public and not await self._user_can_view_group(db, current_user.id, group.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        if include_members:
            return GroupWithMembers.from_orm(group)
        return Group.from_orm(group)
    
    async def list_groups(
        self,
        db: AsyncSession,
        current_user: User,
        page: int = 1,
        size: int = 20,
        search: Optional[str] = None,
        group_type: Optional[str] = None,
        is_public: Optional[bool] = None,
        owner_id: Optional[str] = None,
        order_by: str = "created_at",
        order_direction: str = "desc"
    ) -> GroupListResponse:
        """List groups with filtering and pagination."""
        skip = (page - 1) * size
        
        groups, total = await self.crud.get_groups(
            db=db,
            skip=skip,
            limit=size,
            search=search,
            group_type=group_type,
            is_public=is_public,
            owner_id=owner_id,
            order_by=order_by,
            order_direction=order_direction
        )
        
        # Filter out private groups the user can't access
        accessible_groups = []
        for group in groups:
            if group.is_public or await self._user_can_view_group(db, current_user.id, group.id):
                accessible_groups.append(Group.from_orm(group))
        
        pages = calculate_pagination(page, size, total)
        
        return GroupListResponse(
            groups=accessible_groups,
            total=len(accessible_groups),
            page=page,
            size=size,
            pages=pages["total_pages"]
        )
    
    async def update_group(
        self,
        db: AsyncSession,
        group_id: str,
        group_data: GroupUpdate,
        current_user: User
    ) -> Group:
        """Update a group."""
        # Check permissions
        if not await self._user_can_manage_group(db, current_user.id, group_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to update group"
            )
        
        try:
            group = await self.crud.update_group(
                db=db,
                group_id=group_id,
                group_data=group_data,
                updated_by=current_user.id
            )
            return Group.from_orm(group)
        except NotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found"
            )
        except ConflictError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
    
    async def delete_group(
        self,
        db: AsyncSession,
        group_id: str,
        current_user: User
    ) -> bool:
        """Delete a group."""
        # Check permissions
        if not await self._user_can_manage_group(db, current_user.id, group_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to delete group"
            )
        
        try:
            return await self.crud.delete_group(
                db=db,
                group_id=group_id,
                deleted_by=current_user.id
            )
        except NotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Group not found"
            )
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    async def add_users_to_group(
        self,
        db: AsyncSession,
        group_id: str,
        membership_request: GroupMembershipRequest,
        current_user: User
    ) -> List[UserInGroup]:
        """Add users to a group."""
        # Check permissions
        if not await self._user_can_manage_group(db, current_user.id, group_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to add users to group"
            )
        
        added_users = []
        errors = []
        
        for user_id in membership_request.user_ids:
            try:
                membership = await self.crud.add_user_to_group(
                    db=db,
                    group_id=group_id,
                    user_id=user_id,
                    role_in_group=membership_request.role_in_group,
                    added_by=current_user.id
                )
                
                # Get user info for response
                user_info = await self._get_user_in_group_info(db, user_id, group_id)
                if user_info:
                    added_users.append(user_info)
                    
            except (NotFoundError, ConflictError, ValidationError) as e:
                errors.append(f"User {user_id}: {str(e)}")
        
        if errors and not added_users:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="; ".join(errors)
            )
        
        return added_users
    
    async def remove_user_from_group(
        self,
        db: AsyncSession,
        group_id: str,
        user_id: str,
        current_user: User
    ) -> bool:
        """Remove a user from a group."""
        # Check permissions
        if not await self._user_can_manage_group(db, current_user.id, group_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to remove users from group"
            )
        
        try:
            return await self.crud.remove_user_from_group(
                db=db,
                group_id=group_id,
                user_id=user_id
            )
        except NotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User is not a member of this group"
            )
    
    async def update_user_membership(
        self,
        db: AsyncSession,
        group_id: str,
        user_id: str,
        membership_data: GroupMembershipUpdate,
        current_user: User
    ) -> UserInGroup:
        """Update a user's group membership."""
        # Check permissions
        if not await self._user_can_manage_group(db, current_user.id, group_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions to update group membership"
            )
        
        try:
            await self.crud.update_user_group_membership(
                db=db,
                group_id=group_id,
                user_id=user_id,
                membership_data=membership_data
            )
            
            user_info = await self._get_user_in_group_info(db, user_id, group_id)
            if not user_info:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User membership not found"
                )
            
            return user_info
            
        except NotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User is not a member of this group"
            )
    
    async def get_group_members(
        self,
        db: AsyncSession,
        group_id: str,
        current_user: User,
        page: int = 1,
        size: int = 20,
        role_filter: Optional[str] = None
    ) -> List[UserInGroup]:
        """Get group members."""
        # Check permissions
        if not await self._user_can_view_group(db, current_user.id, group_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        skip = (page - 1) * size
        members, total = await self.crud.get_group_members(
            db=db,
            group_id=group_id,
            skip=skip,
            limit=size,
            role_filter=role_filter
        )
        
        return [
            UserInGroup(
                id=user.id,
                username=user.username,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                role_in_group=membership.role_in_group,
                joined_at=membership.joined_at,
                is_active=membership.is_active
            )
            for user, membership in members
        ]
    
    async def get_user_groups(
        self,
        db: AsyncSession,
        user_id: str,
        current_user: User,
        page: int = 1,
        size: int = 20
    ) -> List[Group]:
        """Get groups that a user is a member of."""
        # Users can only see their own groups unless they're admin
        if user_id != current_user.id and not await self._user_is_admin(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        skip = (page - 1) * size
        groups, total = await self.crud.get_user_groups(
            db=db,
            user_id=user_id,
            skip=skip,
            limit=size
        )
        
        return [Group.from_orm(group) for group, membership in groups]
    
    async def _user_can_view_group(self, db: AsyncSession, user_id: str, group_id: str) -> bool:
        """Check if user can view a group."""
        # Get user's membership or admin status
        members, _ = await self.crud.get_group_members(
            db=db,
            group_id=group_id,
            skip=0,
            limit=1,
            role_filter=None,
            active_only=False
        )
        
        for user, membership in members:
            if user.id == user_id:
                return True
        
        return False
    
    async def _user_can_manage_group(self, db: AsyncSession, user_id: str, group_id: str) -> bool:
        """Check if user can manage a group."""
        group = await self.crud.get_group(db, group_id)
        if not group:
            return False
        
        # Owner can always manage
        if group.owner_id == user_id:
            return True
        
        # Check if user is admin of the group
        members, _ = await self.crud.get_group_members(
            db=db,
            group_id=group_id,
            skip=0,
            limit=1000,  # Get all members to check roles
            role_filter=None,
            active_only=True
        )
        
        for user, membership in members:
            if user.id == user_id and membership.role_in_group == "admin":
                return True
        
        return False
    
    async def _user_is_admin(self, user: User) -> bool:
        """Check if user is a system admin."""
        # This would typically check user's role
        return user.role and user.role.name in ["admin", "super_admin"]
    
    async def _get_user_in_group_info(self, db: AsyncSession, user_id: str, group_id: str) -> Optional[UserInGroup]:
        """Get user information in group context."""
        members, _ = await self.crud.get_group_members(
            db=db,
            group_id=group_id,
            skip=0,
            limit=1000,
            role_filter=None,
            active_only=False
        )
        
        for user, membership in members:
            if user.id == user_id:
                return UserInGroup(
                    id=user.id,
                    username=user.username,
                    email=user.email,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    role_in_group=membership.role_in_group,
                    joined_at=membership.joined_at,
                    is_active=membership.is_active
                )
        
        return None


# Create singleton instance
group_service = GroupService()
