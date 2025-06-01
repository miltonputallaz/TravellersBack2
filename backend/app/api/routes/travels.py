import uuid
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, status, UploadFile, Form, File
from sqlmodel import func, select
from pydantic import EmailStr

from app.api.deps import CurrentUser, SessionDep
from app.models import Item, ItemCreate, ItemPublic, ItemsPublic, ItemUpdate, Message, TravelsPublic, Travel, User, TravelRegister, TravelPublic
from ...core.file_utils import saveFileAndGetId

router = APIRouter(prefix="/travels", tags=["travels"])


@router.get("/", response_model=TravelsPublic)
def read_travels(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve travels.
    """
    travels = []

    for owned_travel in current_user.owned_travels:
        travels.append(TravelPublic(**owned_travel.model_dump(), owner=True))

    for owned_travel in current_user.travels:
        travels.append(TravelPublic(**owned_travel.model_dump()))
    
    
    
    return TravelsPublic(data=travels, count=len(travels))


@router.post("/", status_code = status.HTTP_201_CREATED)
async def create_travel(
    *, session: SessionDep, current_user: CurrentUser, title: str = Form(), description: Optional[str] = Form(None), invited_emails: Optional[list[EmailStr]] = Form(None), file: UploadFile = Optional[File()]
) -> Any:
    """
    Create new item.
    """
    print(f"MIlton -> TItle {title} DEscription {description} Image {file}")
    travelDb = Travel(title=title, description=description)

    if file is not None:
        fileId = await saveFileAndGetId(file, current_user.id)
        if fileId is not None:
            travelDb.imageId = fileId
    
    travelDb.owners.append(current_user)
    
    if invited_emails is not None:
        sentence = select(User)

        for mail in invited_emails:
            sentence = sentence.where(User.email == mail)

        invited_users = session.exec(sentence).all()

        travelDb.users.extend(invited_users)

    session.add(travelDb)
    session.commit()