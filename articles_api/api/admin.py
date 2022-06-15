from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from articles_api.api.dependencies import RolesChecker, get_db, get_admin
from articles_api.core.enums import Roles
from articles_api.core.mapping import db_user_to_user
from articles_api.core.schemas import Article, User
from articles_api.db import crud, models


router = APIRouter()

@router.post("/admin/add_role", response_model=User)
def add_role(user_id: int, role: Roles,
             db: Session = Depends(get_db),
             admin: models.User = Depends(get_admin)
             ) -> User:
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if RolesChecker.have_user_one_of_roles(user, {role}):
        raise HTTPException(status_code=409, detail=f"User already has role {role}")
    crud.add_role(db, user, role)
    return db_user_to_user(user)


@router.post("/admin/remove_role", response_model=User)
def remove_role(user_id: int, role: Roles,
                db: Session = Depends(get_db),
                admin: models.User = Depends(get_admin)
                ) -> User:
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not RolesChecker.have_user_one_of_roles(user, {role}):
        raise HTTPException(status_code=409, detail=f"User does not have role {role}")
    crud.remove_role(db, user, role)
    return db_user_to_user(user) 

#@router.post("/admin/set_active", response_model=User)
#def set_actve(active: bool, user_id: int)