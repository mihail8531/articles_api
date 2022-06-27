from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from articles_api.core import schemas 
from articles_api.core.enums import CommentaryStates, Roles
from articles_api.db import models
from articles_api.api.dependencies import get_db_commentary, get_current_active_user, get_db

router = APIRouter()

router.get("/commentaries/{commentary_id}", response_model=schemas.Commentary)
def get_commentary(db_commentary: models.Commentary=Depends(get_db_commentary),
                   db_user: models.User=Depends(get_current_active_user),
                   db: Session=Depends(get_db)
                   ) -> models.Commentary:
    is_creator = db_commentary.is_creator(db_user)
    is_admin = db_user.have_role(Roles.admin)
    is_moderator = db_user.have_role(Roles.moderator)
    is_reader = db_user.have_role(Roles.reader)
    if is_creator or is_admin:
        return db_commentary
    if is_reader and db_commentary.have_state(CommentaryStates.approved):
        return db_commentary
    if is_moderator and not db_commentary.have_state(CommentaryStates.approved):
        return db_commentary
    raise HTTPException(status_code=403, detail="Access denied")
    
    
    
