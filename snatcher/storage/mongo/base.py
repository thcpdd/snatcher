from typing import Union
from datetime import datetime

import pymongo
from bson import ObjectId as BSONObjectId

from snatcher.conf import settings
from snatcher.utils.hashlib import encrypt_fuel


study_year = settings.SELECT_COURSE_YEAR
term = settings.TERM
period = settings.PERIOD


class MongoDBCollection:
    """
    A MongoDB singleton connection.

    It makes sure subclass has a same mongodb client instance and database instance.
    """
    _client = None
    _database = None

    # Rewriting it in subclass.
    collection_name = None

    def __init__(self):
        if MongoDBCollection._client is None:
            MongoDBCollection._client = pymongo.MongoClient(settings.get_mongodb_uri())
            MongoDBCollection._database = MongoDBCollection._client.get_database("snatcher")
        self.client = MongoDBCollection._client
        self.database = MongoDBCollection._database
        self.collection = self.database.get_collection(self.collection_name)

    def query(self, page: int, size: int = 10, sort=None, **options):
        if hasattr(self, 'params'):
            options.update(self.params)
        total = self.collection.count_documents(options)
        cursor = self.collection.find(options, skip=(page - 1) * size, limit=size, sort=sort)
        return cursor, total

    def query_one(self, *args, **kwargs):
        raise NotImplementedError

    def create(self, *args, **kwargs):
        raise NotImplementedError

    def update(self, *args, **kwargs):
        raise NotImplementedError


class UserMongoDBCollection(MongoDBCollection):
    collection_name = 'user'

    def create(self, username: str, password_hash: str, email: str):
        document = {
            'username': username,
            'password': password_hash,
            'email': email,
            'created_at': datetime.now(),
            'role': 'common',
            'is_deleted': False
        }
        result = self.collection.insert_one(document)
        return result.inserted_id

    def query_one(self, username: str):
        return self.collection.find_one({'username': username})

    def update(self, row_id: BSONObjectId, **options):
        action = {'$set': options}
        self.collection.find_one_and_update({'_id': row_id}, action)


class PCMongoDBCollection(MongoDBCollection):
    collection_name = 'pc'
    params = {
        'study_year': study_year,
        'term': term,
        'period': period
    }

    def create(self, course_name: str, course_id: str, course_no: str):
        document = {
            'course_name': course_name,
            'course_id': course_id,
            'course_no': course_no
        }
        document.update(self.params)
        result = self.collection.insert_one(document)
        return result.inserted_id


class PEMongoDBCollection(MongoDBCollection):
    collection_name = 'pe'
    params = {
        'study_year': study_year,
        'term': term,
    }

    def create(self, course_name: str, course_id: str, grade: int):
        document = {
            'course_name': course_name,
            'course_id': course_id,
            'grade': grade
        }
        document.update(self.params)
        result = self.collection.insert_one(document)
        return result.inserted_id


class EnergyMongoDBCollection(MongoDBCollection):
    collection_name = 'energy'

    def create(self, username: str, key: str):
        document = {
            'username': username,
            'fuel': '',
            'created_at': datetime.now(),
            'status': 'unused'
        }
        result = self.collection.insert_one(document)
        row_id = result.inserted_id
        fuel = encrypt_fuel(str(row_id), key)
        self.collection.find_one_and_update({'_id': row_id}, {'$set': {'fuel': fuel}})
        return fuel

    def update(self, row_id: BSONObjectId, status: str):
        action = {'$set': {'status': status}}
        self.collection.find_one_and_update({'_id': row_id}, action)

    def query_one(self, row_id: BSONObjectId):
        return self.collection.find_one({"_id": row_id})


class FailureMongoDBCollection(MongoDBCollection):
    collection_name = 'failure'

    def create(self, username: str, course_name: str, log_key: str, port: int, reason: str):
        document = {
            'username': username,
            'course_name': course_name,
            'log_key': log_key,
            'port': port,
            'reason': reason,
            'created_at': datetime.now()
        }
        result = self.collection.insert_one(document)
        return result.inserted_id


class SubmittedMongoDBCollection(MongoDBCollection):
    collection_name = 'submitted'

    def create(self, username: str, email: str, course_name: str, log_key: str):
        document = {
            'username': username,
            'email': email,
            'course_name': course_name,
            'log_key': log_key,
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'success': 0
        }
        result = self.collection.insert_one(document)
        return result.inserted_id

    def update(self, row_id: BSONObjectId, **options):
        options.update({'updated_at': datetime.now()})
        action = {'$set': options}
        self.collection.find_one_and_update({'_id': row_id}, action)


class SecurityMongoDBCollection(MongoDBCollection):
    collection_name = 'security'

    def create(self, key: str, purpose: str):
        document = {
            'key': key,
            'purpose': purpose,
            'created_at': datetime.now(),
            'is_deleted': False
        }
        result = self.collection.insert_one(document)
        return result.inserted_id

    def query_one(self, purpose: str):
        cursor = self.collection.find(
            {'purpose': purpose, 'is_deleted': False},
            sort={'created_at': -1}
        )
        return cursor.next()['key']


MongoDBCollectionTyping = Union[
    UserMongoDBCollection,
    PCMongoDBCollection,
    PEMongoDBCollection,
    EnergyMongoDBCollection,
    FailureMongoDBCollection,
    SubmittedMongoDBCollection,
    SecurityMongoDBCollection
]


class MongoDBCollections:
    """
    A MongoDB collection manager.

    Usage:
        collections = MongoDBCollections()
        collection = collections['collection_name']
    """
    collection_mapping = {
        'user': UserMongoDBCollection,
        'pc': PCMongoDBCollection,
        'pe': PEMongoDBCollection,
        'energy': EnergyMongoDBCollection,
        'failure': FailureMongoDBCollection,
        'submitted': SubmittedMongoDBCollection,
        'security': SecurityMongoDBCollection
    }
    collection_instances = {}

    def __getitem__(self, collection_name: str) -> MongoDBCollectionTyping | None:
        if collection_name not in self.collection_instances:
            if collection_name not in self.collection_mapping:
                collection_instance = None
            else:
                collection_instance = self.collection_mapping[collection_name]()
                self.collection_instances[collection_name] = collection_instance
        else:
            collection_instance = self.collection_instances[collection_name]
        return collection_instance

    def get(self, collection_name: str, default=None) -> MongoDBCollectionTyping | None:
        return self[collection_name] or default
