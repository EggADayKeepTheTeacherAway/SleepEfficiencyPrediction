import unittest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

class BasicSeleniumTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        options = Options()
        cls.driver = webdriver.Chrome(service=Service(), options=options)
        cls.driver.implicitly_wait(10)

    def test_example_com_title(self):
        self.driver.get("https://example.com")
        self.assertIn("Example Domain", self.driver.title)

    def test_example_com_heading(self):
        self.driver.get("https://example.com")
        heading = self.driver.find_element(By.TAG_NAME, "h1").text
        self.assertEqual(heading, "Example Domain")

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main()
