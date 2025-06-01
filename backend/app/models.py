import uuid

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

class UserTravelLink(SQLModel, table=True):
    user_id: uuid.UUID | None = Field(default=None, foreign_key="travel.id", primary_key=True)
    travel_id: uuid.UUID | None = Field(default=None, foreign_key="user.id", primary_key=True)

class OwnerTravelLink(SQLModel, table=True):
    user_id: uuid.UUID | None = Field(default=None, foreign_key="user.id", primary_key=True)
    travel_id: uuid.UUID | None = Field(default=None, foreign_key="travel.id", primary_key=True)

# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
    travels: list["Travel"] = Relationship(back_populates="users", link_model=UserTravelLink)
    owned_travels: list["Travel"] = Relationship(back_populates="owners", link_model=OwnerTravelLink)


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class TravelBase(SQLModel):
    title: str = Field(nullable = False, min_length = 1, max_length=255)
    description: str | None = Field(default=None, max_length=255)
    imageId: str | None = Field(default=None)
    
class TravelBaseIdentified(TravelBase):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
class Travel(TravelBaseIdentified, table=True):
    owners: list[User] = Relationship(back_populates="owned_travels", link_model=OwnerTravelLink)
    users: list[User] = Relationship(back_populates="travels", link_model=UserTravelLink)

class TravelRegister(TravelBase):
    invited_emails: list[EmailStr] | None = Field(default= None)

# Properties to return via API, id is always required
class TravelPublic(TravelBaseIdentified):
    owner: bool = False


class TravelsPublic(SQLModel):
    data: list[TravelPublic]
    count: int

# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    title: str = Field(max_length=255)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)
