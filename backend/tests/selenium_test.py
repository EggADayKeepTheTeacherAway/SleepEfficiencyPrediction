from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# Create a new instance of the Chrome driver
driver = webdriver.Chrome('./chromedriver')

# Open the Python website
driver.get("https://www.python.org")

# Print the page title
print(driver.title)



# Find the search bar using its name attribute

search_bar = driver.find_element_by_name("q")

search_bar.clear()

search_bar.send_keys("getting started with python")

search_bar.send_keys(Keys.RETURN)



# Print the current URL

print(driver.current_url)



# Close the browser window

driver.close()