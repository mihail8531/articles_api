from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from articles_api.core import schemas 
from articles_api.core.enums import CommentaryStates, Roles
from articles_api.db import models
from articles_api.api.dependencies import get_db_commentary, get_current_active_user, get_db

router = APIRouter()

router.get("/commentaries/{commentary_id}", response_model=schemas.Commentary)
def get_commentary(db_commentary=Depends(get_db_commentary),
                   db_user=Depends(get_current_active_user),
                   db: Session=Depends(get_db)
                   ) -> models.Commentary:
    is_creator = db_user.id == db_commentary.creator_id
    is_admin = Roles.admin in db_user.roles
    is_moderator = Roles.moderator in db_user.roles
    is_reader = Roles.reader in db_user.roles
    if is_creator or is_admin:
        return db_commentary
    if is_reader and db_commentary.state == CommentaryStates.approved:
        return db_commentary
    if is_moderator and db_commentary.state != CommentaryStates.approved:
        return db_commentary
    raise HTTPException(status_code=403, detail="Access denied")
    
    
    
