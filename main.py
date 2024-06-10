from dotenv import load_dotenv
import os
import time
import requests

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.chrome import ChromeType


load_dotenv()


email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")
searched_string = os.getenv("SEARCH_STRING") or "choux"
webhook = os.getenv("SLACK_HOOK_URL")
notify_failure = os.getenv("NOTIFY_FAILURE") == "true"

option = Options()
option.page_load_strategy = "normal"
option.add_argument("--disable-infobars")
option.add_argument("start-maximized")
option.add_argument("--disable-extensions")
option.add_argument("--headless")
option.add_argument("--no-sandbox")
option.add_argument("--window-size=1920,1080")
option.add_argument("--accept-lang=fr")


service = Service(ChromeDriverManager().install())
print(service)
driver = webdriver.Chrome(service=service, options=option)
print(f"Driver: {driver}")

driver.get("https://abris-securises-velos.paris.fr/login")

# Login
login_el = driver.find_element(By.XPATH, '//input[@name="email"]')
password_el = driver.find_element(By.XPATH, '//input[@name="password"]')
login_el.send_keys(email)
password_el.send_keys(password)
driver.find_element(By.XPATH, '//button[@type="submit"]').submit()

time.sleep(5)

driver.get("https://abris-securises-velos.paris.fr/waiting-lists")

time.sleep(30)


elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{searched_string}')]")
elements2 = driver.find_elements(
    By.XPATH, f"//*[contains(text(), '{searched_string.lower()}')]"
)

all_elements = elements + elements2

if len(all_elements) > 0:
    payload = {"text": f"✅ Found {searched_string} in Paris Bike SaS list"}
    response = requests.post(webhook, json=payload)
elif notify_failure:
    payload = {"text": f"❌ Did not found {searched_string} in Paris Bike SaS list"}
    response = requests.post(webhook, json=payload)

driver.quit()
