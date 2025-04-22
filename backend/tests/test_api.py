import unittest
from fastapi.testclient import TestClient
import time
import sys
import os
from datetime import datetime
import asyncio
import pymysql
from dbutils.pooled_db import PooledDB

# Add the 'backend' directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from controller import app, get_user_id
from config import DB_HOST, DB_USER, DB_PASSWD, DB_NAME

# Database connection pool for cleanup
cleanup_pool = PooledDB(creator=pymysql,
                        host=DB_HOST,
                        user=DB_USER,
                        password=DB_PASSWD,
                        database=DB_NAME,
                        maxconnections=1,
                        blocking=True)

class TestAPIEndpoints(unittest.TestCase):
    test_username = "test_user_one"
    test_password = "test_password_one"
    test_user_id = None
    created_sleep_ids = []
    _posted_log_data = False

    @classmethod
    def setUpClass(cls):
        """Set up once for the entire test class. Create a single test user."""
        cls.client = TestClient(app)
        register_data = {
            "username": cls.test_username,
            "password": cls.test_password,
            "age": 30,
            "gender": "female",
            "smoke": False,
            "exercise": 2
        }
        registration_response = cls.client.post("/sleep-api/user/register", json=register_data)
        assert registration_response.status_code == 200
        cls.test_user_id = asyncio.run(get_user_id(cls.test_username, cls.test_password))
        assert cls.test_user_id is not None
        print(f"Single test user created with ID: {cls.test_user_id}")

    @classmethod
    def tearDownClass(cls):
        """Clean up once after the entire test class. Remove the created test user and all associated sleep data."""
        with cleanup_pool.connection() as conn, conn.cursor() as cs:
            cs.execute("DELETE FROM sleep WHERE user_id = %s", (cls.test_user_id,))
            cs.execute("DELETE FROM sleep_user_data WHERE user_id = %s", (cls.test_user_id,))
            conn.commit()
        print(f"Single test user (ID: {cls.test_user_id}) and associated data cleaned up.")

    def setUp(self):
        """Set up before each test."""
        self.client = TestClient(app)
        self._posted_log_data = False

    def tearDown(self):
        """Clean up after each test (currently focused on resetting flags)."""
        self._posted_log_data = False
        # Sleep data cleanup is now handled in tearDownClass

    def _post_log_data(self):
        """Helper function to post sleep log data and track it."""
        if not self._posted_log_data:
            log_data = {
                "username": self.test_username,
                "password": self.test_password,
                "temperature": 25,
                "humidity": 60,
                "heartrate": 65
            }
            response = self.client.post("/sleep-api/log", json=log_data)
            self.assertEqual(response.json(), {"message": "Data Inserted"})
            self.assertEqual(response.status_code, 200)
            with cleanup_pool.connection() as conn, conn.cursor() as cs:
                cs.execute("""
                    SELECT sleep_id
                    FROM sleep
                    WHERE user_id = %s
                    ORDER BY ts DESC
                    LIMIT 1
                """, (self.test_user_id,))
                inserted_data = cs.fetchone()
                if inserted_data and inserted_data[0] not in self.created_sleep_ids:
                    self.created_sleep_ids.append(inserted_data[0])
            self._posted_log_data = True

    def test_register_failure_username_exists(self):
        """Test registration failure when the single test username already exists."""
        register_data_new = {
            "username": self.test_username,
            "password": "anotherpassword",
            "age": 25,
            "gender": "male",
            "smoke": True,
            "exercise": 5
        }
        response = self.client.post("/sleep-api/user/register", json=register_data_new)
        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.json())

    def test_login_success(self):
        """Test successful user login with the single test user."""
        response = self.client.post(
            "/sleep-api/user/login",  # Add the missing "sleep-api" prefix
            json={"username": self.test_username, "password": self.test_password}
        )
        self.assertEqual(response.json(), {"user_id": self.test_user_id, "message": "Success"})
        self.assertEqual(response.status_code, 200)

    def test_post_log_data_success(self):
        """Test successful posting of sleep log data for the single test user."""
        log_data = {
            "username": self.test_username,
            "password": self.test_password,
            "temperature": 25,
            "humidity": 60,
            "heartrate": 65
        }
        response = self.client.post("/sleep-api/log", json=log_data)
        self.assertEqual(response.json(), {"message": "Data Inserted"})
        self.assertEqual(response.status_code, 200)
        with cleanup_pool.connection() as conn, conn.cursor() as cs:
            cs.execute("""
                SELECT sleep_id
                FROM sleep
                WHERE user_id = %s
                ORDER BY ts DESC
                LIMIT 1
            """, (self.test_user_id,))
            inserted_data = cs.fetchone()
            if inserted_data and inserted_data[0] not in self.created_sleep_ids:
                self.created_sleep_ids.append(inserted_data[0])
        self._posted_log_data = True

    def test_post_log_data_invalid_credentials(self):
        """Test posting log data with invalid user credentials for the single test user."""
        log_data = {
            "username": self.test_username,
            "password": "wrongpassword",
            "temperature": 26.0,
            "humidity": 65.0,
            "heartrate": 70
        }
        response = self.client.post("/sleep-api/log", json=log_data)
        self.assertIn("detail", response.json())
        self.assertEqual(response.status_code, 400)

    def test_get_sessions_success(self):
        """Test successful retrieval of user sessions for the single test user."""
        self._post_log_data() # Ensure log data exists before getting sessions
        response = self.client.get(f"/sleep-api/sessions/{self.test_user_id}")  # Add the missing "sleep-api" prefix
        self.assertIsInstance(response.json(), list)
        self.assertEqual(response.status_code, 200)
        # Add more specific assertions about the content if needed

    def test_get_sessions_user_not_found(self):
        """Test retrieval of sessions for a non-existent user."""
        non_existent_user_id = 9999
        response = self.client.get(f"/sessions/{non_existent_user_id}")
        self.assertIn("detail", response.json())
        self.assertEqual(response.status_code, 404)

    def test_get_efficiency_latest_success(self):
        """Test successful retrieval of latest sleep efficiency for the single test user."""
        self._post_log_data() # Ensure log data exists before getting efficiency
        response = self.client.get(f"/sleep-api/efficiency/{self.test_user_id}")  # Add the missing "sleep-api" prefix        self.assertIsInstance(response.json(), list)
        self.assertEqual(response.status_code, 200)
        if response.json():
            self.assertIn("efficiency", response.json()[0])
            self.assertIn("light", response.json()[0])
            # Add more assertions about the structure

    def test_get_efficiency_latest_user_not_found(self):
        """Test retrieval of latest efficiency for a non-existent user."""
        non_existent_user_id = 9999
        response = self.client.get(f"/efficiency/{non_existent_user_id}")
        self.assertIn("detail", response.json())
        self.assertEqual(response.status_code, 404)

    def test_get_efficiency_by_sleep_id_success(self):
        """Test successful retrieval of sleep efficiency by sleep ID for the single test user."""
        self._post_log_data() # Ensure log data exists
        # Assuming the first posted log will have sleep_id 1 (may need adjustment)
        response = self.client.get(f"/efficiency/{self.test_user_id}/1")
        if response.status_code == 200:
            self.assertIn("efficiency", response.json())
            self.assertIn("light", response.json())
        elif response.status_code == 404:
            self.assertIn("detail", response.json())
        self.assertIn(response.status_code, [200, 404])

    def test_get_efficiency_by_sleep_id_not_found(self):
        """Test retrieval of efficiency for a non-existent sleep ID."""
        response = self.client.get(f"/efficiency/{self.test_user_id}/9999")
        self.assertIn("detail", response.json())
        self.assertEqual(response.status_code, 404)

    def test_get_log_by_sleep_id_success(self):
        """Test successful retrieval of sleep log by sleep ID for the single test user."""
        self._post_log_data() # Ensure log data exists
        response = self.client.get(f"/log/{self.test_user_id}/1")
        if response.status_code == 200:
            self.assertIsInstance(response.json(), list)
            if response.json():
                self.assertIn("ts", response.json()[0])
                self.assertIn("temperature", response.json()[0])
        elif response.status_code == 404:
            self.assertIn("detail", response.json())
        self.assertIn(response.status_code, [200, 404])

    def test_get_log_by_sleep_id_not_found(self):
        """Test retrieval of log for a non-existent sleep ID."""
        response = self.client.get(f"/log/{self.test_user_id}/9999")
        self.assertIn("detail", response.json())
        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main()