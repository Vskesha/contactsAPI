"""
Routes for the contacts.
"""
from typing import List, Optional, Type

from fastapi import Path, Depends, HTTPException, Query, status, APIRouter
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User, Contact
from src.repository import contacts as repos_contacts
from src.services.auth import auth_service
from src.schemas import ContactModel, ContactFavoriteModel, ContactResponse

router = APIRouter(prefix="/contacts", tags=["contact"])


@router.get("/", response_model=List[ContactResponse],
            description="Get a list of the current user's contacts."
                        " No more than 10 requests per minute.",
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_contacts(
        skip: int = 0,
        limit: int = Query(default=10, le=100, ge=10),
        favorite: bool = None,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)) -> List[Type[Contact]]:
    """
    Get a list of the current user's contacts.

    :param skip: Number of contacts to skip.
    :type skip: int
    :param limit: Number of contacts to retrieve.
    :type limit: int
    :param favorite: Favorite flag of the contact.
    :type favorite: bool
    :param db: The database session.
    :type db: Session
    :param current_user: The current authenticated user.
    :type current_user: User
    :return: List of contacts.
    :rtype: List[Type[Contact]]
    """
    contacts = await repos_contacts.get_contacts(user=current_user, db=db, skip=skip,
                                                 limit=limit, favorite=favorite)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse,
            description='No more than 10 requests per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)) -> Contact:
    """
    Get a single contact by ID.

    :param contact_id: ID of the contact to retrieve.
    :type contact_id: int
    :param db: The database session.
    :type db: Session
    :param current_user: The current authenticated user.
    :type current_user: User
    :return: The contact with the specified ID.
    :rtype: Contact
    """
    contact = await repos_contacts.get_contact_by_id(contact_id, db, current_user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return contact


@router.post("", response_model=ContactResponse, status_code=status.HTTP_201_CREATED,
             description='No more than 10 creations per minute',
             dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def create_contact(body: ContactModel, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)) -> Contact:
    """
    Create a new contact.

    :param body: parameters of the contact to create.
    :type body: ContactModel
    :param db: The database session.
    :type db: Session
    :param current_user: The current authenticated user.
    :type current_user: User
    :return: The created contact.
    :rtype: Contact
    """
    contact = await repos_contacts.get_contact_by_email(body.email, db, current_user)
    if contact:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=f"Email already exists!"
        )
    try:
        contact = await repos_contacts.create(body, db, current_user)
    except IntegrityError as err:
        raise HTTPException(
            status_code=status.HTTP_404_INVALID_REQUEST, detail=f"Error: {err}"
        )
    return contact


@router.put("/{contact_id}", response_model=ContactResponse,
            description='No more than 10 updates per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def update_contact(body: ContactModel,
                         contact_id: int = Path(ge=1),
                         db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)) -> Contact:
    """
    Update an existing contact of current authenticated user.

    :param body: parameters of the contact to update.
    :type body: ContactModel
    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param db: The database session.
    :type db: Session
    :param current_user: The current authenticated user.
    :type current_user: User
    :return: Updated contact.
    :rtype: Contact
    """
    contact = await repos_contacts.update(contact_id, body, db, current_user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return contact


@router.patch("/{contact_id}/favorite", response_model=ContactResponse,
              description='No more than 10 updates per minute',
              dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def favorite_update(body: ContactFavoriteModel,
                          contact_id: int = Path(ge=1),
                          db: Session = Depends(get_db),
                          current_user: User = Depends(auth_service.get_current_user)) -> Contact:
    """
    Update favorite status of an existing contact of current authenticated user.
    :param body: parameters of the contact to update.
    :type body: ContactModel
    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param db: The database session.
    :type db: Session
    :param current_user: The current authenticated user.
    :type current_user: User
    :return: Updated contact.
    :rtype: Contact
    """
    contact = await repos_contacts.favorite_update(contact_id, body, db, current_user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT,
               description='No more than 10 deletions per minute',
               dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def remove_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)) -> None:
    """
    Delete an existing contact of current authenticated user.

    :param contact_id: The ID of the contact to delete.
    :type contact_id: int
    :param db: The database session.
    :type db: Session
    :param current_user: The current authenticated user.
    :type current_user: User
    :return: None
    """
    contact = await repos_contacts.delete(contact_id, db, current_user)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return None


@router.get("/search/{query}", response_model=List[ContactResponse],
            summary="Search contacts by name, lastname, email",
            description='No more than 10 searches per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def search_by(query: Optional[str] = None, db: Session = Depends(get_db),
                    current_user: User = Depends(auth_service.get_current_user)) -> List[Type[Contact]]:
    """
    Search contacts by name, lastname, email.

    :param query: Parameters of the search.
    :type query: Optional[str]
    :param db: The database session.
    :type db: Session
    :param current_user: The current authenticated user.
    :type current_user: User
    :return: List of contacts with the specified parameters.
    :rtype: List[Type[Contact]]
    """
    contacts = await repos_contacts.search_contacts(query, db, current_user)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact Not Found")

    return contacts


@router.get("/birthdays/next_week", response_model=List[ContactResponse],
            description='No more than 10 searches per minute',
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def search_contacts(days: int = Query(default=7, le=30, ge=1),
                          skip: int = 0,
                          limit: int = Query(default=10, le=30, ge=1),
                          db: Session = Depends(get_db),
                          current_user: User = Depends(auth_service.get_current_user)) -> List[Type[Contact]]:
    """
    Finds contacts with birthday in the next specified number of days.

    :param days: Number of days in the future from today.
    :type days: int
    :param skip: Number of contacts to skip.
    :type skip: int
    :param limit: Number of contacts to retrieve.
    :type limit: int
    :param db: The database session.
    :type db: Session
    :param current_user: The current authenticated user.
    :type current_user: User
    :return: List of contacts.
    :rtype: List[Type[Contact]]

    """
    contacts = None
    if days:
        par = {
            "days": days,
            "skip": skip,
            "limit": limit,
        }
        contacts = await repos_contacts.search_birthday(par, db, current_user)
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No contacts found")
    return contacts
