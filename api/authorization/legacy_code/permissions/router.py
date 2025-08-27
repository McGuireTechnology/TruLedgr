from fastapi import APIRouter, HTTPException, Depends, Body
from ..models import User
from ..auth.auth import get_current_user
from fastapi_security_sample.db import get_db
from .. import service
from ..logging import LoggingRoute, log_user_action


router = APIRouter(route_class=LoggingRoute)


# Permission management endpoints
@router.post("", response_model=dict)
async def create_permission(
    permission_data: dict = Body(...),
    db=Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new permission (admin only)"""
    if not await service.user_has_permission(db, current_user.id, "permissions", "create"):
        raise HTTPException(status_code=403, detail="Not authorized to create permissions")
    
    try:
        permission = await service.create_permission(
            db,
            permission_data["permission_id"],
            permission_data["name"],
            permission_data["resource"],
            permission_data["action"],
            permission_data.get("description")
        )
        log_user_action("create_permission", current_user.id, {"permission_name": permission_data['name']})
        return {"message": "Permission created successfully", "permission": permission}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list)
async def list_permissions(
    db=Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all permissions"""
    try:
        permissions = await service.list_permissions(db)
        return permissions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resource/{resource}", response_model=list)
async def get_permissions_by_resource(
    resource: str,
    db=Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get permissions by resource"""
    try:
        permissions = await service.get_permissions_by_resource(db, resource)
        return permissions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{user_id}", response_model=list)
async def get_user_permissions(
    user_id: str,
    db=Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user permissions (users can only access their own permissions unless admin)"""
    if current_user.id != user_id and not await service.user_has_permission(db, current_user.id, "users", "read"):
        raise HTTPException(status_code=403, detail="Not authorized to view other user's permissions")
    
    try:
        permissions = await service.get_user_permissions(db, user_id)
        return permissions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
