import unittest
from fastapi.testclient import TestClient
from backend.controller import app

class Test_USER_API(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_register_user(self):
        response = self.client.post("/sleep-api/user/register", json={
            "username": "testuser",
            "password": "testpass",
            "age": 25,
            "gender": "male",
            "smoke": False,
            "exercise": 3
        })
        self.assertIn(response.status_code, [200, 400])  # 400 if username exists
        print("Register:", response.json())

    def test_login_user(self):
        response = self.client.post("/sleep-api/user/login", json={
            "username": "testuser",
            "password": "testpass"
        })
        self.assertIn(response.status_code, [200, 400])
        print("Login:", response.json())

    def test_edit_user(self):
        response = self.client.post("/sleep-api/user/edit", json={
            "user_id": 1,  # Adjust this to your test user_id
            "username": "testuser",
            "password": "newpass",
            "age": 26,
            "gender": "male",
            "smoke": True,
            "exercise": 2
        })
        self.assertIn(response.status_code, [200, 400])
        print("Edit:", response.json())

    def test_get_latest(self):
        response = self.client.get("/sleep-api/latest/1")  # Adjust user_id
        self.assertIn(response.status_code, [200, 404])
        print("Latest:", response.json())

    def test_get_efficiency(self):
        response = self.client.get("/sleep-api/efficiency/1")  # Adjust user_id
        self.assertIn(response.status_code, [200, 400])
        print("Efficiency:", response.json())

    def test_get_efficiency_by_sleep_id(self):
        response = self.client.get("/sleep-api/efficiency/1/1")  # Adjust user_id and sleep_id
        self.assertIn(response.status_code, [200, 400])
        print("Efficiency by sleep_id:", response.json())

    def test_get_log(self):
        response = self.client.get("/sleep-api/log/1")  # Adjust user_id
        self.assertIn(response.status_code, [200, 400])
        print("Log:", response.json())

    def test_get_sessions(self):
        response = self.client.get("/sleep-api/sessions/1")  # Adjust user_id
        self.assertIn(response.status_code, [200, 400])
        print("Sessions:", response.json())


if __name__ == '__main__':
    unittest.main()
