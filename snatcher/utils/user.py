from .hashlib import password_hash
from ..storage.mongo import collections, ObjectId, get_security_key


def authenticate(username: str, password: str):
    user_collection = collections['user']
    db_user = user_collection.query_one(username)
    if db_user is None:
        return False
    if db_user['is_deleted']:
        return False
    salt = get_security_key('password')
    if db_user['password'] != password_hash(password, salt):
        return False
    return True


def create_user(username: str, password: str, email: str) -> ObjectId:
    """Creating a user and return the user id."""
    user_collection = collections['user']
    salt = get_security_key('password')
    user_id = user_collection.create(
        username=username,
        password_hash=password_hash(password, salt),
        email=email
    )
    return user_id
