# All other imports stay the same
import unittest
from time import sleep
import warnings
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests


chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()
streamlit_url = "http://localhost:8501"
api_url = "http://127.0.0.1:8080/sleep-api"
test_username = 'testusername'
test_password = "testpassword123"
test_age = 30
test_gender = "female"
test_smoke = 'Yes'
test_exercise = 3
user_id = None

def wait_for_element(by, value, timeout=2):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )

def navigate_to_page(page_name):
    print(f"Looking for header with text: {page_name}")
    nav_option = wait_for_element(
        By.XPATH,
        f"//label[.//div[@data-testid='stMarkdownContainer']//p[contains(text(), '{page_name}')]]"
    )
    nav_option.click()



driver.get(streamlit_url)
sleep(1)
try:
    register_radio = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((
            By.XPATH,
            "//label[.//div[@data-testid='stMarkdownContainer']//p[text()='Register']]"
        ))
    )
    register_radio.click()
    print("Clicked 'Register' radio button.")
    sleep(1)
except Exception as e:
    print("Error:", e)

print("Registering User")
navigate_to_page("Register")
sleep(2)
wait_for_element(By.CSS_SELECTOR, "input[aria-label='Username']").send_keys(test_username)
wait_for_element(By.CSS_SELECTOR, "input[aria-label='Password']").send_keys(test_password)
age_input = wait_for_element(By.CSS_SELECTOR, "input[aria-label='How old are you']")
age_input.clear()
age_input.send_keys(str(test_age))

from selenium.webdriver.common.action_chains import ActionChains

# Scroll to and click the label to open the dropdown
gender_label = driver.find_element(By.XPATH, "//input[contains(@aria-label, 'What gender are you?')]")
gender_label.click()

# Wait for the dropdown option "male" to appear
wait = WebDriverWait(driver, 2)
wait.until(EC.visibility_of_element_located((By.XPATH, f"//div[text()='{test_gender}']")))

# Click on the "male" option
female_option = driver.find_element(By.XPATH, f"//div[text()='{test_gender}']")
ActionChains(driver).move_to_element(female_option).click().perform()

# wait_for_element(By.XPATH, f"//div[contains(@class, 'streamlit-selectbox')]//div[contains(text(), '{test_gender}')]").click()

smoke_dropdown = driver.find_element(By.XPATH, "//input[contains(@aria-label, 'Do you smoke?')]")
smoke_dropdown.click()

wait = WebDriverWait(driver, 2)
wait.until(EC.visibility_of_element_located((By.XPATH, f"//div[text()='{test_smoke}']")))

smoke_option = driver.find_element(By.XPATH, f"//div[text()='{test_smoke}']")
ActionChains(driver).move_to_element(smoke_option).click().perform()
sleep(2)

exercise_input = wait_for_element(By.CSS_SELECTOR, "input[aria-label='Exercise sessions per week']")
exercise_input.clear()
exercise_input.send_keys(str(test_exercise))

sleep(2)
wait_for_element(By.XPATH, "//button[.//p[text()='Register']]")
print('I found it yo.')

# success_message = wait_for_element(By.XPATH, "//div[contains(@class, 'stAlert')]//p[contains(text(), 'Registration successful')]")


# response = requests.post(f"{api_url}/user/login", json={
#     "username": test_username,
#     "password": test_password
# })
# response.raise_for_status()
# user_id = response.json().get("user_id")
