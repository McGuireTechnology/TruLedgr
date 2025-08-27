"""
Groups API router.

This module defines the FastAPI routes for group management operations,
including CRUD operations and membership management.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.groups.service import group_service
from api.groups.schemas import (
    GroupCreate, GroupUpdate, Group, GroupWithMembers,
    GroupMembershipRequest, GroupMembershipUpdate,
    UserInGroup, GroupListResponse
)
from api.db.deps import get_async_session
from api.authentication.deps import get_current_active_user
from api.users.models import User

router = APIRouter(
    prefix="/groups",
    tags=["groups"],
    responses={404: {"description": "Not found"}}
)


@router.post("", response_model=Group, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_data: GroupCreate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new group.
    
    - **name**: Group name (required)
    - **description**: Group description
    - **is_public**: Whether the group is publicly visible
    - **is_open**: Whether users can join without approval
    - **group_type**: Type of group (general, department, project, etc.)
    - **tags**: Comma-separated tags
    - **max_members**: Maximum number of members
    """
    return await group_service.create_group(
        db=db,
        group_data=group_data,
        current_user=current_user
    )


@router.get("", response_model=GroupListResponse)
async def list_groups(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search in name, description, or tags"),
    group_type: Optional[str] = Query(None, description="Filter by group type"),
    is_public: Optional[bool] = Query(None, description="Filter by public/private"),
    owner_id: Optional[str] = Query(None, description="Filter by owner"),
    order_by: str = Query("created_at", description="Order by field"),
    order_direction: str = Query("desc", regex="^(asc|desc)$", description="Order direction"),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    List groups with filtering and pagination.
    
    Returns paginated list of groups that the user can access.
    """
    return await group_service.list_groups(
        db=db,
        current_user=current_user,
        page=page,
        size=size,
        search=search,
        group_type=group_type,
        is_public=is_public,
        owner_id=owner_id,
        order_by=order_by,
        order_direction=order_direction
    )


@router.get("/{group_id}", response_model=Group)
async def get_group(
    group_id: str,
    include_members: bool = Query(False, description="Include member list"),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific group by ID.
    
    - **group_id**: Group ID
    - **include_members**: Whether to include member information
    """
    return await group_service.get_group(
        db=db,
        group_id=group_id,
        current_user=current_user,
        include_members=include_members
    )


@router.get("/slug/{slug}", response_model=Group)
async def get_group_by_slug(
    slug: str,
    include_members: bool = Query(False, description="Include member list"),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific group by slug.
    
    - **slug**: Group slug (URL-friendly name)
    - **include_members**: Whether to include member information
    """
    return await group_service.get_group_by_slug(
        db=db,
        slug=slug,
        current_user=current_user,
        include_members=include_members
    )


@router.put("/{group_id}", response_model=Group)
async def update_group(
    group_id: str,
    group_data: GroupUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a group.
    
    Only group owners and admins can update groups.
    """
    return await group_service.update_group(
        db=db,
        group_id=group_id,
        group_data=group_data,
        current_user=current_user
    )


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: str,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a group.
    
    Only group owners can delete groups.
    System groups cannot be deleted.
    """
    await group_service.delete_group(
        db=db,
        group_id=group_id,
        current_user=current_user
    )


@router.get("/{group_id}/members", response_model=List[UserInGroup])
async def get_group_members(
    group_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    role_filter: Optional[str] = Query(None, description="Filter by role in group"),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get group members.
    
    Returns paginated list of group members with their roles.
    """
    return await group_service.get_group_members(
        db=db,
        group_id=group_id,
        current_user=current_user,
        page=page,
        size=size,
        role_filter=role_filter
    )


@router.post("/{group_id}/members", response_model=List[UserInGroup], status_code=status.HTTP_201_CREATED)
async def add_users_to_group(
    group_id: str,
    membership_request: GroupMembershipRequest,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Add users to a group.
    
    - **user_ids**: List of user IDs to add
    - **role_in_group**: Role to assign (member, admin, moderator, viewer)
    
    Only group owners and admins can add users.
    """
    return await group_service.add_users_to_group(
        db=db,
        group_id=group_id,
        membership_request=membership_request,
        current_user=current_user
    )


@router.delete("/{group_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user_from_group(
    group_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Remove a user from a group.
    
    Only group owners and admins can remove users.
    """
    await group_service.remove_user_from_group(
        db=db,
        group_id=group_id,
        user_id=user_id,
        current_user=current_user
    )


@router.put("/{group_id}/members/{user_id}", response_model=UserInGroup)
async def update_user_membership(
    group_id: str,
    user_id: str,
    membership_data: GroupMembershipUpdate,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a user's group membership.
    
    - **role_in_group**: New role for the user
    - **is_active**: Whether the membership is active
    
    Only group owners and admins can update memberships.
    """
    return await group_service.update_user_membership(
        db=db,
        group_id=group_id,
        user_id=user_id,
        membership_data=membership_data,
        current_user=current_user
    )


@router.get("/users/{user_id}/groups", response_model=List[Group])
async def get_user_groups(
    user_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get groups that a user is a member of.
    
    Users can only see their own groups unless they're admin.
    """
    return await group_service.get_user_groups(
        db=db,
        user_id=user_id,
        current_user=current_user,
        page=page,
        size=size
    )


@router.get("/test")
async def test_groups_endpoint():
    """Simple test endpoint to verify Groups router is working."""
    return {"message": "Groups router is working!", "status": "ok"}
