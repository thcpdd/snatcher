import pymongo

from snatcher.conf import settings


class MongoDBConnection:
    """
    A MongoDB singleton connection.

    It makes sure subclass has a same mongodb client instance and database instance.
    """
    _client = None
    _database = None

    # Rewriting it in subclass.
    collection_name = None

    def __init__(self):
        if MongoDBConnection._client is None:
            MongoDBConnection._client = pymongo.MongoClient(settings.get_mongodb_uri())
            MongoDBConnection._database = MongoDBConnection._client.get_database("snatcher")
        self.client = MongoDBConnection._client
        self.database = MongoDBConnection._database
        self.collection = self.database.get_collection(self.collection_name)


class UserMongoDBConnection(MongoDBConnection):
    collection_name = 'user'


class PCMongoDBConnection(MongoDBConnection):
    collection_name = 'pc'


class PEMongoDBConnection(MongoDBConnection):
    collection_name = 'pe'


class EnergyMongoDBConnection(MongoDBConnection):
    collection_name = 'energy'


class FailureMongoDBConnection(MongoDBConnection):
    collection_name = 'failure'


class SubmittedMongoDBConnection(MongoDBConnection):
    collection_name = 'submitted'


class SecurityMongoDBConnection(MongoDBConnection):
    collection_name = 'security'
