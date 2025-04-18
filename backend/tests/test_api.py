import unittest
from fastapi.testclient import TestClient
import sys
import os

# Add the 'backend' directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.controller import app  # Import 'app' from 'backend/controller.py'
from datetime import datetime

class TestAPIEndpoints(unittest.TestCase):
    def setUp(self):
        """Set up for each test. Initialize TestClient."""
        self.client = TestClient(app)

    def test_login_success(self):
        """Test successful user login."""
        response = self.client.post(
            "/user/login",
            json={"username": "testuser", "password": "testpassword"}  # Replace with a test user
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Success"})

    def test_login_failure_invalid_credentials(self):
        """Test login failure with invalid credentials."""
        response = self.client.post(
            "/user/login",
            json={"username": "testuser", "password": "wrongpassword"}
        )
        self.assertEqual(response.status_code, 401)
        self.assertIn("detail", response.json())

    def test_register_success(self):
        """Test successful user registration."""
        new_username = f"newuser_{datetime.now().timestamp()}"  # Unique username
        response = self.client.post(
            "/user/register",
            json={
                "username": new_username,
                "password": "newpassword",
                "age": 30,
                "gender": "female",
                "smoke": False,
                "exercise": 2
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "User Registered"})

    def test_register_failure_username_exists(self):
        """Test registration failure when username already exists."""
        response = self.client.post(
            "/user/register",
            json={
                "username": "testuser",  # Use an existing username
                "password": "anotherpassword",
                "age": 25,
                "gender": "male",
                "smoke": True,
                "exercise": 5
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.json())

    def test_get_sessions_success(self):
        """Test successful retrieval of user sessions."""
        user_id = 1  # Replace with a valid user ID that has sessions
        response = self.client.get(f"/sessions/{user_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        # Add more specific assertions about the content if needed

    def test_get_sessions_user_not_found(self):
        """Test retrieval of sessions for a non-existent user."""
        user_id = 9999  # Replace with a non-existent user ID
        response = self.client.get(f"/sessions/{user_id}")
        self.assertEqual(response.status_code, 404)
        self.assertIn("detail", response.json())

    def test_get_efficiency_latest_success(self):
        """Test successful retrieval of latest sleep efficiency."""
        user_id = 1  # Replace with a valid user ID
        response = self.client.get(f"/efficiency/{user_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        if response.json():
            self.assertIn("efficiency", response.json()[0])
            self.assertIn("light", response.json()[0])
            # Add more assertions about the structure

    def test_get_efficiency_latest_user_not_found(self):
        """Test retrieval of latest efficiency for a non-existent user."""
        user_id = 9999
        response = self.client.get(f"/efficiency/{user_id}")
        self.assertEqual(response.status_code, 404)
        self.assertIn("detail", response.json())

    def test_get_efficiency_by_sleep_id_success(self):
        """Test successful retrieval of sleep efficiency by sleep ID."""
        user_id = 1  # Replace with a valid user ID
        sleep_id = 1  # Replace with a valid sleep ID for that user
        response = self.client.get(f"/efficiency/{user_id}/{sleep_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("efficiency", response.json())
        self.assertIn("light", response.json())
        # Add more assertions

    def test_get_efficiency_by_sleep_id_not_found(self):
        """Test retrieval of efficiency for a non-existent sleep ID."""
        user_id = 1
        sleep_id = 9999
        response = self.client.get(f"/efficiency/{user_id}/{sleep_id}")
        self.assertEqual(response.status_code, 404)
        self.assertIn("detail", response.json())

    def test_get_log_by_sleep_id_success(self):
        """Test successful retrieval of sleep log by sleep ID."""
        user_id = 1  # Replace with a valid user ID
        sleep_id = 1  # Replace with a valid sleep ID for that user
        response = self.client.get(f"/log/{user_id}/{sleep_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        if response.json():
            self.assertIn("ts", response.json()[0])
            self.assertIn("temperature", response.json()[0])
            # Add more assertions about the log data structure

    def test_get_log_by_sleep_id_not_found(self):
        """Test retrieval of log for a non-existent sleep ID."""
        user_id = 1
        sleep_id = 9999
        response = self.client.get(f"/log/{user_id}/{sleep_id}")
        self.assertEqual(response.status_code, 404)
        self.assertIn("detail", response.json())

if __name__ == "__main__":
    unittest.main()