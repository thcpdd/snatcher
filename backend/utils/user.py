import jwt
from fastapi import Request, HTTPException

from .tools import delay_time
from .validators import ObjectId
from snatcher.utils.hashlib import password_hash
from snatcher.storage.mongo import collections, get_security_key
from backend.response import ResponseCodes, tuple2dict


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
    return db_user


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


def identity_validator(request: Request):
    token = request.headers.get('Authorization')
    if not token:
        raise HTTPException(401, detail=tuple2dict(ResponseCodes.ILLEGAL_REQUEST))
    secret = get_security_key('jwt')
    try:
        jwt.decode(token, secret, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, detail=tuple2dict(ResponseCodes.INVALID_IDENTITY))
    except jwt.InvalidTokenError:
        raise HTTPException(401, detail=tuple2dict(ResponseCodes.INVALID_TOKEN))


def login(username: str, password: str):
    user = authenticate(username, password)
    if not user:
        return None
    exp = delay_time(hours=5)
    secret = get_security_key('jwt')
    token = jwt.encode({'username': username, 'exp': exp}, secret, algorithm='HS256')
    return token
