from pymongo import MongoClient
from pymongo.results import DeleteResult, UpdateResult
from ...config.settings import Settings




class MongoDatabase:

    
    __database_instance = None

    @staticmethod
    def get_database():
        if MongoDatabase.__database_instance is None:    
            client = MongoClient(Settings.MONGODB_URI)
            database = client[Settings.MONGODB_DB_NAME]
            if database is None:
                raise Exception("Database connection failed")
            
            MongoDatabase.__database_instance = database
        
        return MongoDatabase.__database_instance

    @staticmethod
    def insert_one(collection: str, document: dict):
        db = MongoDatabase.get_database()
        return db[collection].insert_one(document)
    
    @staticmethod
    def find_one(collection: str, query: dict):
        db = MongoDatabase.get_database()
        return db[collection].find_one(query)

    @staticmethod
    def find(collection: str, query: dict, sort: list = [], limit: int = 0):
        db = MongoDatabase.get_database()
        cursor = db[collection].find(query, sort=sort, limit=limit)
        return cursor.to_list()
    @staticmethod
    def delete_one(collection: str, query: dict) -> DeleteResult:
        db = MongoDatabase.get_database()
        return db[collection].delete_one(query)

    @staticmethod
    def delete_many(collection: str, query: dict) -> DeleteResult:
        db = MongoDatabase.get_database()
        return db[collection].delete_many(query)
    
    @staticmethod
    def update_one(collection: str, query: dict, update: dict) -> UpdateResult:
        db = MongoDatabase.get_database()
        return db[collection].update_one(query, {'$set': update})
    
    @staticmethod
    def update_many(collection: str, query: dict, update: dict) -> UpdateResult:
        db = MongoDatabase.get_database()
        return db[collection].update_many(query, {'$set': update})