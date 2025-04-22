# All other imports stay the same
import unittest
import time
import warnings
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests


# Global driver and config
driver = webdriver.Chrome()
driver.get("http://localhost:8501")  # Load only once


class SmartSleepTrackerE2ETests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = driver  # Use the global driver
        cls.streamlit_url = "http://localhost:8501"
        cls.driver.maximize_window()
        warnings.simplefilter("ignore", ResourceWarning)
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        cls.api_url = "http://127.0.0.1:8080/sleep-api"
        cls.test_username = f"testuser_{int(time.time())}"
        cls.test_password = "testpassword123"
        cls.test_age = 30
        cls.test_gender = "male"
        cls.test_smoke = "No"
        cls.test_exercise = 3
        cls.user_id = None

    @classmethod
    def tearDownClass(cls):
        if cls.user_id is not None:
            try:
                requests.post(f"{cls.api_url}/user/delete", json={
                    "user_id": cls.user_id,
                    "username": cls.test_username,
                    "password": cls.test_password
                })
            except Exception:
                pass


    def setUp(self):
        self.wait_for_element(By.TAG_NAME, "h1")

    def wait_for_element(self, by, value, timeout=2):
        return WebDriverWait(self.__class__.driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def navigate_to_page(self, page_name):
        print(f"Looking for header with text: {page_name}")
        nav_option = self.wait_for_element(
                                        By.XPATH,
                                        f"//label[.//div[@data-testid='stMarkdownContainer']//p[contains(text(), '{page_name}')]]"
                                        )
        nav_option.click()
        # header = self.wait_for_element(By.XPATH, f"//h1[contains(text(), '{page_name}') or contains(text(), 'User Registration')]")
        # self.assertTrue(header.is_displayed())

    def login_user(self):
        username_input = self.wait_for_element(By.CSS_SELECTOR, "input[aria-label='Username']")
        self.clear_field(username_input)
        username_input.send_keys(self.test_username)

        password_input = self.wait_for_element(By.CSS_SELECTOR, "input[aria-label='Password']")
        self.clear_field(password_input)
        password_input.send_keys(self.test_password)

        login_button = self.wait_for_element(By.XPATH, "//button[.//p[text()='Login']]")
        login_button.click()
        try:
            logged_in_text = self.wait_for_element(By.XPATH, f"//div[@data-testid='stMarkdownContainer']//p[contains(text(), 'Logged in as: {self.test_username}')]")
            self.assertTrue(logged_in_text.is_displayed())
        except (TimeoutException, NoSuchElementException):
            success_message = self.wait_for_element(By.XPATH, f"//div[contains(@class, 'stAlert')]//p[contains(text(), 'Logged in as {self.test_username}')]")
            self.assertTrue(success_message.is_displayed())

        if self.__class__.user_id is None:
            try:
                response = requests.post(f"{self.api_url}/user/login", json={
                    "username": self.test_username,
                    "password": self.test_password
                })
                response.raise_for_status()
                self.__class__.user_id = response.json().get("user_id")
            except Exception as e:
                self.fail(f"Failed to get user_id after login: {str(e)}")

    def clear_field(self, component):
        component.send_keys(Keys.COMMAND + "a")
        component.send_keys(Keys.BACKSPACE)

    def test_01_user_registration(self):
        print("Registering User")
        self.navigate_to_page("Register")
        time.sleep(1)
        username_input = self.wait_for_element(By.CSS_SELECTOR, "input[aria-label='Username']")
        username_input.send_keys(self.__class__.test_username)
        password_input = self.wait_for_element(By.CSS_SELECTOR, "input[aria-label='Password']")
        password_input.send_keys(self.__class__.test_password)        
        age_input = self.wait_for_element(By.CSS_SELECTOR, "input[aria-label='How old are you']")
        self.clear_field(age_input)
        age_input.send_keys(str(self.__class__.test_age))

        # Scroll to and click the label to open the dropdown
        gender_label = driver.find_element(By.XPATH, "//input[contains(@aria-label, 'What gender are you?')]")
        gender_label.click()

        # Gender
        self.wait_for_element(By.XPATH, f"//div[text()='{self.__class__.test_gender}']")
        gender_option = driver.find_element(By.XPATH, f"//div[text()='{self.__class__.test_gender}']")
        ActionChains(driver).move_to_element(gender_option).click().perform()

        # Smoke
        self.wait_for_element(By.XPATH, f"//div[text()='{self.__class__.test_smoke}']")
        smoke_option = driver.find_element(By.XPATH, f"//div[text()='{self.__class__.test_smoke}']")
        ActionChains(driver).move_to_element(smoke_option).click().perform()

        # Exercise
        exercise_input = self.wait_for_element(By.CSS_SELECTOR, "input[aria-label='Exercise sessions per week']")
        self.clear_field(exercise_input)
        exercise_input.send_keys(str(self.__class__.test_exercise))

        # time.sleep(2)
        self.wait_for_element(By.XPATH, "//button[.//p[text()='Register']]").click()
        success_message = self.wait_for_element(By.XPATH, "//div[contains(@class, 'stAlert')]//p[contains(text(), 'Registration successful')]")
        self.assertTrue(success_message.is_displayed())

        response = requests.post(f"{self.api_url}/user/login", json={
            "username": self.test_username,
            "password": self.test_password
        })
        response.raise_for_status()
        self.__class__.user_id = response.json().get("user_id")
        self.assertIsNotNone(self.__class__.user_id)

    def test_02_user_login(self):
        self.navigate_to_page("Overview")
        self.login_user()

    def test_03_user_logout(self):
        self.driver.get(self.streamlit_url)
        self.login_user()
        logout_button = self.wait_for_element(By.XPATH, "//button[.//p[text()='Logout']]")
        logout_button.click()
        login_button = self.wait_for_element(By.XPATH, "//button[.//p[text()='Login']]")
        self.assertTrue(login_button.is_displayed())

    def test_04_user_login(self):
        self.driver.get(self.streamlit_url)
        self.navigate_to_page("Overview")
        self.login_user()

    def test_05_send_sensor_data(self):
        if self.__class__.user_id is None:
            self.test_01_user_registration()
            self.test_04_user_login()
        for i in range(5):
            sensor_data = {
                "username": self.test_username,
                "password": self.test_password,
                "temperature": 22 + i,
                "humidity": 55 - i,
                "heartrate": 68 + i
            }
            try:
                response = requests.post(f"{self.api_url}/log", json=sensor_data)
                response.raise_for_status()
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json().get("message"), "Data Inserted")
                time.sleep(2)
            except requests.exceptions.RequestException as e:
                self.fail(f"Failed to send sensor data: {str(e)}")

        try:
            response = requests.get(f"{self.api_url}/latest/{self.__class__.user_id}")
            response.raise_for_status()
            latest = response.json()
            self.assertGreaterEqual(latest["temperature"], 22)
            self.assertLessEqual(latest["temperature"], 26)
            self.assertGreaterEqual(latest["humidity"], 50)
            self.assertLessEqual(latest["humidity"], 51)
            self.assertGreaterEqual(latest["heartrate"], 72)
            self.assertLessEqual(latest["heartrate"], 73)
        except Exception as e:
            self.fail(f"Failed to retrieve latest data: {str(e)}")

    def test_06_check_sleep_sessions(self):
        if self.__class__.user_id is None:
            self.test_01_user_registration()
            self.test_04_user_login()
            self.test_05_send_sensor_data()
        try:
            response = requests.get(f"{self.api_url}/sessions/{self.__class__.user_id}")
            response.raise_for_status()
            sessions = response.json()
            print("session : ", sessions)
            self.assertGreater(len(sessions), 0)
            self.driver.get(self.streamlit_url)
            self.login_user()
            self.navigate_to_page("Dashboard")
            try:
                selector = self.wait_for_element(By.XPATH, "//p[contains(text(), 'Select Sleep Session')]")
                self.assertTrue(selector.is_displayed())
            except (TimeoutException, NoSuchElementException):
                alert = self.wait_for_element(By.XPATH, "//div[contains(@class, 'stAlert')]")
                self.assertTrue(alert.is_displayed())
        except Exception as e:
            self.fail(f"Failed to fetch sessions: {str(e)}")

    def test_07_check_sleep_efficiency(self):
        if self.__class__.user_id is None:
            self.test_01_user_registration()
            self.test_04_user_login()
            self.test_05_send_sensor_data()
            self.test_06_check_sleep_sessions()
        try:
            response = requests.get(f"{self.api_url}/efficiency/{self.__class__.user_id}")
            response.raise_for_status()
            efficiencies = response.json()
            self.assertGreater(len(efficiencies), 0)
            for eff in efficiencies:
                self.assertGreaterEqual(eff["light"], 0)
                self.assertLessEqual(eff["light"], 1)
                self.assertGreaterEqual(eff["rem"], 0)
                self.assertLessEqual(eff["rem"], 1)
                self.assertGreaterEqual(eff["deep"], 0)
                self.assertLessEqual(eff["deep"], 1)
                self.assertGreaterEqual(eff["efficiency"], 0)
                self.assertLessEqual(eff["efficiency"], 1)
                self.assertGreaterEqual(eff["sleep_duration"], 0)
                datetime.strptime(eff["start_time"], "%d-%m-%Y %H:%M:%S")
                datetime.strptime(eff["end_time"], "%d-%m-%Y %H:%M:%S")
            self.driver.get(self.streamlit_url)
            self.login_user()
            self.navigate_to_page("Prediction")
            try:
                self.assertTrue(self.wait_for_element(By.XPATH, "//p[contains(text(), 'Select Session')]").is_displayed())
                self.assertTrue(self.wait_for_element(By.XPATH, "//p[contains(text(), 'Sleep Efficiency')]").is_displayed())
            except (TimeoutException, NoSuchElementException):
                self.assertTrue(self.wait_for_element(By.XPATH, "//div[contains(@class, 'stAlert')]").is_displayed())
        except Exception as e:
            self.fail(f"Failed to retrieve efficiency data: {str(e)}")

    def test_08_check_sleep_log(self):
        if self.__class__.user_id is None:
            self.test_01_user_registration()
            self.test_04_user_login()
            self.test_05_send_sensor_data()
        try:
            sessions = requests.get(f"{self.api_url}/sessions/{self.__class__.user_id}").json()
            sleep_id = sessions[0]['sleep_id']
            log_data = requests.get(f"{self.api_url}/log/{self.__class__.user_id}/{sleep_id}").json()
            self.assertGreater(len(log_data), 0)
            for item in log_data:
                self.assertEqual(item["user_id"], self.__class__.user_id)
                self.assertEqual(item["sleep_id"], sleep_id)
                datetime.strptime(item["ts"], "%d-%m-%Y %H:%M:%S")
                self.assertGreaterEqual(item["temperature"], 15)
                self.assertLessEqual(item["temperature"], 35)
                self.assertGreaterEqual(item["humidity"], 30)
                self.assertLessEqual(item["humidity"], 80)
                self.assertGreaterEqual(item["heartrate"], 40)
                self.assertLessEqual(item["heartrate"], 120)
        except Exception as e:
            self.fail(f"Failed to retrieve log data: {str(e)}")

    def test_09_user_logout(self):
        self.driver.get(self.streamlit_url)
        self.login_user()
        logout_button = self.wait_for_element(By.XPATH, "//button[.//p[text()='Logout']]")
        logout_button.click()
        login_button = self.wait_for_element(By.XPATH, "//button[.//p[text()='Login']]")
        self.assertTrue(login_button.is_displayed())

    def test_10_api_validation(self):
        invalid_register = {
            "username": self.test_username + "_invalid",
            "password": self.test_password,
            "age": -5,
            "gender": "invalid",
            "smoke": False,
            "exercise": 10
        }
        try:
            response = requests.post(f"{self.api_url}/user/register", json=invalid_register)
            self.assertEqual(response.status_code, 400)
            invalid_sensor = {
                "username": self.test_username,
                "password": self.test_password,
                "temperature": "not a number",
                "humidity": 999,
                "heartrate": -50
            }
            response = requests.post(f"{self.api_url}/log", json=invalid_sensor)
            self.assertNotEqual(response.status_code, 200)
        except requests.exceptions.RequestException:
            pass

if __name__ == "__main__":
    unittest.main()
    driver.quit()