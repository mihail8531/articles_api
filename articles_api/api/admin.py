from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from articles_api.api.dependencies import RolesChecker, get_db, get_admin, get_db_user
from articles_api.core import schemas
from articles_api.core.enums import Roles
from articles_api.core.mapping import db_user_to_user
from articles_api.db import crud, models


router = APIRouter()

@router.patch("/admin/add_role", response_model=schemas.User)
def add_role(role: Roles,
             db_user: models.User = Depends(get_db_user),
             db: Session = Depends(get_db),
             admin: models.User = Depends(get_admin)
             ) -> schemas.User:
    if RolesChecker.have_user_one_of_roles(db_user, {role}):
        raise HTTPException(status_code=409, detail=f"User already has role {role}")
    crud.add_role(db, db_user, role)
    return db_user_to_user(db_user)


@router.delete("/admin/remove_role", response_model=schemas.User)
def remove_role(role: Roles,
                db_user: models.User = Depends(get_db_user),
                db: Session = Depends(get_db),
                admin: models.User = Depends(get_admin)) -> schemas.User:
    if not RolesChecker.have_user_one_of_roles(db_user, {role}):
        raise HTTPException(status_code=409, detail=f"User does not have role {role}")
    crud.remove_role(db, db_user, role)
    return db_user_to_user(db_user) 

@router.patch("/admin/set_active", response_model=schemas.User)
def set_actve(is_active: bool, 
              db_user: models.User = Depends(get_db_user),
              admin: models.User = Depends(get_admin),
              db: Session = Depends(get_db)) -> schemas.User:
    crud.set_user_active(db, db_user, is_active)
    return db_user_to_user(db_user)
