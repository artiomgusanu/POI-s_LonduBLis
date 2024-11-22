from selenium import webdriver
from selenium.webdriver.firefox.service import Service

# Path to GeckoDriver
gecko_path = "C:\\POI-s_LonduBlis\\Scraping\\geckodriver.exe"  # Update this path

# Initialize Firefox WebDriver
service = Service(gecko_path)
driver = webdriver.Firefox(service=service)

# Open a test page
driver.get("https://www.google.com")
print("Firefox launched successfully!")

# Close the browser
driver.quit()
