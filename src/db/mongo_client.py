from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError


class MongoDBClient:
    def __init__(self, uri, db_name):
        """
        Initialize the MongoDB client.

        :param uri: MongoDB connection string.
        :param db_name: Name of the database to use.
        """
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def insert_data(self, collection_name, data):
        """
        Insert a document into a MongoDB collection.

        :param collection_name: The collection to insert data into.
        :param data: The document to insert.
        :return: True if inserted, False if duplicate.
        """
        collection = self.db[collection_name]
        try:
            # Ensure unique entries (requires unique index on title + url)
            collection.insert_one(data)
            return True
        except DuplicateKeyError:
            return False

    def fetch_data(self, collection_name, query=None, projection=None):
        """
        Fetch data from a MongoDB collection.

        :param collection_name: The collection to fetch data from.
        :param query: The query to filter data.
        :param projection: The fields to include or exclude.
        :return: List of documents.
        """
        collection = self.db[collection_name]
        return list(collection.find(query or {}, projection))

    def update_data(self, collection_name, filter_query, update_data):
        """
        Update a document in a MongoDB collection.

        :param collection_name: The collection to update data in.
        :param filter_query: The query to filter documents.
        :param update_data: The update to apply.
        :return: The result of the update operation.
        """
        collection = self.db[collection_name]
        return collection.update_one(filter_query, {'$set': update_data})

    def delete_data(self, collection_name, query):
        """
        Delete documents from a MongoDB collection.

        :param collection_name: The collection to delete data from.
        :param query: The query to filter documents for deletion.
        :return: The result of the delete operation.
        """
        collection = self.db[collection_name]
        return collection.delete_many(query)

    def create_unique_index(self, collection_name, fields):
        """
        Create a unique index for a collection.

        :param collection_name: The collection to create an index on.
        :param fields: A list of tuples specifying fields and sort order.
        """
        collection = self.db[collection_name]
        collection.create_index(fields, unique=True)

    def close_connection(self):
        """
        Close the MongoDB connection.
        """
        self.client.close()
