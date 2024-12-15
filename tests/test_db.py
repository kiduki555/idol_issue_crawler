import unittest
from src.db.mongo_client import MongoDBClient

class TestDB(unittest.TestCase):
    def setUp(self):
        self.db_client = MongoDBClient(uri="mongodb://localhost:27017", db_name="test_db")

    def tearDown(self):
        self.db_client.client.drop_database("test_db")

    def test_insert_data(self):
        data = {"title": "Test Title", "url": "http://example.com", "source": "test"}
        result = self.db_client.insert_data("test_collection", data)
        self.assertTrue(result, "Data should be inserted successfully.")

    def test_fetch_data(self):
        data = {"title": "Test Title", "url": "http://example.com", "source": "test"}
        self.db_client.insert_data("test_collection", data)
        fetched = self.db_client.fetch_data("test_collection")
        self.assertEqual(len(fetched), 1, "Data should be fetched successfully.")

    def test_update_data(self):
        data = {"title": "Test Title", "url": "http://example.com", "source": "test"}
        self.db_client.insert_data("test_collection", data)
        result = self.db_client.update_data("test_collection", {"title": "Test Title"}, {"source": "updated"})
        self.assertEqual(result.modified_count, 1, "Data should be updated successfully.")

    def test_delete_data(self):
        data = {"title": "Test Title", "url": "http://example.com", "source": "test"}
        self.db_client.insert_data("test_collection", data)
        result = self.db_client.delete_data("test_collection", {"title": "Test Title"})
        self.assertEqual(result.deleted_count, 1, "Data should be deleted successfully.")

if __name__ == "__main__":
    unittest.main()
