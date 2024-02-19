"""
Functions for working with users in the database.
"""
from typing import Type

from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> Type[User] | None:
    """
    Retrieves a single user with the specified email.

    :param email: The email of the user to retrieve.
    :type email: str
    :param db: The database session.
    :type db: Session
    :return: The user with the specified email, or None if it does not exist.
    :rtype: User | None
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    Creates a new user.

    :param body: The data for the user to create.
    :type body: UserModel
    :param db: The database session.
    :type db: Session
    :return: The newly created user.
    :rtype: User
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)
    new_user = User(**body.dict(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    Updates token of a single user with the specified ID.

    :param user: The user to update.
    :type user: User
    :param token: The new token for the user.
    :type token: str | None
    :param db: The database session.
    :type db: Session
    :return: None
    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    Sets a user's email confirmed status to True.

    :param email: The email of the user to update.
    :type email: str
    :param db: The database session.
    :type db: Session
    :return: None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def update_avatar(email: str, url: str, db: Session) -> Type[User]:
    """
    Updates avatar of a single user with given email.
    :param email: The email of the user.
    :type email: str
    :param url: Link to the new avatar.
    :type url: str
    :param db: The database session.
    :type db: Session
    :return: User with updated avatar.
    :rtype: Type[User]
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
