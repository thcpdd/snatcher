from functools import lru_cache

from snatcher.utils.hashlib import decrypt_fuel
from .base import MongoDBCollections, BSONObjectId


collections = MongoDBCollections()


@lru_cache()
def get_security_key(purpose: str):
    security_collection = collections['security']
    return security_collection.query_one(purpose)


def get_fuel_status(username: str, fuel: str):
    key = get_security_key('fuel')
    row_id = decrypt_fuel(fuel, key)
    energy_collection = collections['energy']
    energy = energy_collection.query_one(BSONObjectId(row_id))
    if not energy:
        return False
    if energy['username'] != username:
        return False
    return energy['status']


def update_fuel_status(fuel_id: BSONObjectId, status: str):
    energy_collection = collections['energy']
    energy_collection.update(fuel_id, status=status)
