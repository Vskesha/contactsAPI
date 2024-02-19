"""
Functions for retrieving contacts and writing them to the database
"""
from typing import List, Type

from datetime import datetime
from typing import Union

from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from src.database.models import Contact, User
from src.schemas import ContactModel


async def get_contacts(user: User, db: Session, skip: int, limit: int, favorite: Union[bool, None] = None) -> List[
    Type[Contact]]:
    """
    Retrieves a list of contacts for a specific user with specified pagination parameters

    :param user: The user to retrieve contacts for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :param skip: The number of contacts to skip.
    :type skip: int
    :param limit: The maximum number of contacts to return.
    :type limit: int
    :param favorite: Favorite contact flag.
    :type favorite: bool
    :return: A list of contacts.
    :rtype: List[Type[Contact]]
    """
    query = db.query(Contact).filter_by(user_id=user.id)
    if favorite is not None:
        query = query.filter_by(favorite=favorite)
    contact = query.offset(skip).limit(limit).all()
    return contact


async def get_contact_by_id(contact_id: int, db: Session, user: User) -> Contact | None:
    """
    Retrieves a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param db: The database session.
    :type db: Session
    :param user: The user to retrieve the contact for.
    :type user: User
    :return: The contact with the specified ID, or None if it does not exist.
    :rtype: Contact | None
    """
    contact = db.query(Contact).filter(and_(Contact.id == contact_id, Contact.user_id == user.id)).first()
    return contact


async def get_contact_by_email(email: str, db: Session, user: User) -> Contact | None:
    """
    Retrieves a single contact with the specified email for a specific user.

    :param email: The email of the contact to retrieve.
    :type email: str
    :param db: The database session.
    :type db: Session
    :param user: The user to retrieve the contact for.
    :type user: User
    :return: The contact with the specified email, or None if it does not exist.
    :rtype: Contact | None
    """
    contact = db.query(Contact).filter(and_(Contact.email == email, Contact.user_id == user.id)).first()
    return contact


async def create(body: ContactModel, db: Session, user: User) -> Contact:
    """
    Creates a new contact for a specific user.

    :param body: The data for the contact to create.
    :type body: ContactModel
    :param db: The database session.
    :type db: Session
    :param user: The user to create the contact for.
    :type user: User
    :return: The newly created contact.
    :rtype: Contact
    """
    contact = Contact(
        first_name=body.first_name,
        last_name=body.last_name,
        email=body.email,
        phone=body.phone,
        birthday=body.birthday,
        comments=body.comments,
        favorite=body.favorite,
        user_id=user.id
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update(contact_id: int, body: ContactModel, db: Session, user: User) -> Contact | None:
    """
    Updates a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the note to update.
    :type contact_id: int
    :param body: The updated data for the contact.
    :type body: ContactModel
    :param db: The database session.
    :type db: Session
    :param user: The user to update the contact for.
    :type user: User
    :return: The updated contact or None if it does not exist.
    :rtype: Contact | None
    """
    contact = await get_contact_by_id(contact_id, db, user)
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday
        contact.comments = body.comments
        contact.favorite = body.favorite
        db.commit()
    return contact


async def favorite_update(contact_id: int, body: ContactModel, db: Session, user: User) -> Contact | None:
    """
    Updates a favorite flag of single contact with the specified ID for a specific user.
    :param contact_id: The ID of the note to update.
    :type contact_id: int
    :param body: The updated data for the contact.
    :type body: ContactModel
    :param db: The database session.
    :type db: Session
    :param user: The user to update the contact for.
    :type user: User
    :return: The updated contact or None if it does not exist.
    :rtype: Contact | None
    """
    contact = await get_contact_by_id(contact_id, db, user)
    if contact:
        contact.favorite = body.favorite
        db.commit()
    return contact


async def delete(contact_id, db: Session, user: User) -> Contact | None:
    """
    Removes a single contact with the specified ID for a specific user.
    :param contact_id: The ID of the note to update.
    :type contact_id: int
    :param db: The database session.
    :type db: Session
    :param user: The user to update the contact for.
    :type user: User
    :return: The removed contact, or None if it does not exist.
    :rtype: Contact | None
    """
    contact = await get_contact_by_id(contact_id, db, user)
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def search_contacts(query: str, db: Session, user: User) -> List[Type[Contact]]:
    """
    Retrieves a list of contacts for a specific user with specified query parameters

    :param query: String of fields to search for.
    :type query: str
    :param db: The database session.
    :type db: Session
    :param user: The user to update the contact for.
    :type user: User
    :return: A list of contacts.
    :rtype: List[Type[Contact]]
    """
    contacts = db.query(Contact).filter_by(user_id=user.id).filter(
        func.lower(Contact.first_name).contains(func.lower(query)) |
        func.lower(Contact.last_name).contains(func.lower(query)) |
        func.lower(Contact.email).contains(func.lower(query))
    ).all()
    return contacts


async def search_birthday(par: dict, db: Session, user: User) -> List[Type[Contact]]:
    """
    Retrieves a list of contacts for a specific user with specified number of days ahead.

    :param par: dictionary with number of days ahead to search for.
    :type par: dict
    :param db: The database session.
    :type db: Session
    :param user: The user to update the contact for.
    :type user: User
    :return: A list of contacts with the birthday in range of given number of days.
    :rtype: List[Type[Contact]]
    """
    days_param = par.get("days", 7)
    days = int(days_param)
    days += 1
    now = datetime.now().date()
    birthdays_contacts = []
    query = db.query(Contact).filter_by(user_id=user.id)
    contacts = query.offset(par.get("skip")).limit(par.get("limit"))

    for contact in contacts:
        birthday = contact.birthday
        if birthday:
            birthday_this_year = birthday.replace(year=now.year)
            days_until_birthday = (birthday_this_year - now).days
            if days_until_birthday in range(days):
                birthdays_contacts.append(contact)
    return birthdays_contacts
