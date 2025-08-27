from fastapi import APIRouter, HTTPException, Depends, Body
from ..models import User
from ..auth.auth import get_current_user
from fastapi_security_sample.db import get_db
from .. import service
from ..logging import LoggingRoute, log_user_action


router = APIRouter(route_class=LoggingRoute)


# Role management endpoints
@router.post("", response_model=dict)
async def create_role(
    role_data: dict = Body(...),
    db=Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new role (admin only)"""
    # Check if user has admin permission
    if not await service.user_has_permission(db, current_user.id, "roles", "create"):
        raise HTTPException(status_code=403, detail="Not authorized to create roles")
    
    try:
        role = await service.create_role(
            db, 
            role_data["role_id"], 
            role_data["name"], 
            role_data.get("description")
        )
        log_user_action("create_role", current_user.id, {"role_name": role_data['name']})
        return {"message": "Role created successfully", "role": role}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=list)
async def list_roles(
    db=Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all roles"""
    try:
        roles = await service.list_roles(db)
        return roles
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{role_id}/permissions/{permission_id}")
async def assign_permission_to_role(
    role_id: str,
    permission_id: str,
    db=Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign permission to role (admin only)"""
    if not await service.user_has_permission(db, current_user.id, "roles", "modify"):
        raise HTTPException(status_code=403, detail="Not authorized to modify roles")
    
    try:
        success = await service.assign_permission_to_role(db, role_id, permission_id)
        if success:
            log_user_action("assign_permission", current_user.id, {"permission_id": permission_id, "role_id": role_id})
            return {"message": "Permission assigned successfully"}
        else:
            raise HTTPException(status_code=404, detail="Role or permission not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{role_id}/permissions/{permission_id}")
async def remove_permission_from_role(
    role_id: str,
    permission_id: str,
    db=Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove permission from role (admin only)"""
    if not await service.user_has_permission(db, current_user.id, "roles", "modify"):
        raise HTTPException(status_code=403, detail="Not authorized to modify roles")
    
    try:
        success = await service.remove_permission_from_role(db, role_id, permission_id)
        if success:
            log_user_action("remove_permission", current_user.id, {"permission_id": permission_id, "role_id": role_id})
            return {"message": "Permission removed successfully"}
        else:
            raise HTTPException(status_code=404, detail="Role or permission not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# User role assignment endpoints
@router.post("/users/{user_id}/assign/{role_id}")
async def assign_role_to_user(
    user_id: str,
    role_id: str,
    db=Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign role to user (admin only)"""
    if not await service.user_has_permission(db, current_user.id, "users", "modify"):
        raise HTTPException(status_code=403, detail="Not authorized to modify user roles")
    
    try:
        user = await service.assign_role_to_user(db, user_id, role_id)
        if user:
            log_user_action("assign_role", current_user.id, {"role_id": role_id, "user_id": user_id})
            return {"message": "Role assigned successfully", "user": user.dict()}
        else:
            raise HTTPException(status_code=404, detail="User or role not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/users/{user_id}/remove")
async def remove_role_from_user(
    user_id: str,
    db=Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove role from user (admin only)"""
    if not await service.user_has_permission(db, current_user.id, "users", "modify"):
        raise HTTPException(status_code=403, detail="Not authorized to modify user roles")
    
    try:
        user = await service.remove_role_from_user(db, user_id)
        if user:
            log_user_action("remove_role", current_user.id, {"user_id": user_id})
            return {"message": "Role removed successfully", "user": user.dict()}
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
