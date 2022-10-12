import lxml
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from twilio.rest import Client
from webdriver_manager.chrome import ChromeDriverManager

TWILIO_ACCOUNT_SID = "AC1a50bd2ea7e62d5d7bb7ee9afd86690c"
TWILIO_AUTH_TOKEN = "dfa2fd6f9802bacef2778829e5081f79"
TWILIO_NUMBER = "+13854798422"
MY_NUMBER = "+16193437689"
TRENDING_TICKERS_URL = "https://finance.yahoo.com/lookup/"
response = requests.get(TRENDING_TICKERS_URL)
content = response.text
soup = BeautifulSoup(content, "lxml")
ticker_list = soup.find(name="tbody").find_all(name="a", class_="Fw(b)")
ticker_endpoints = {(t.get_text(), t.get("href")) for t in ticker_list[:5]}

options = Options()
options.headless = True
options.add_argument("log-level=3")
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()), options=options
)
msg = ""
quote_url = ""
for t in ticker_endpoints:
    quote_url = t[1]
    driver.get(f"https://finance.yahoo.com{quote_url}")
    prev_close = driver.find_element(By.XPATH, "//td[@data-test='PREV_CLOSE-value']")
    current_value = driver.find_element(
        By.XPATH, "//fin-streamer[@data-test='qsp-price']"
    )
    change_value = driver.find_element(
        By.XPATH, "//fin-streamer[@data-test='qsp-price-change']"
    )
    per_change_value = driver.find_element(
        By.XPATH, "//fin-streamer[@data-field='regularMarketChangePercent']"
    )
    msg += f"\n{t[0]}, Previous close: {prev_close.text}, Current: {current_value.text} ({change_value.text}) {per_change_value.text}"
driver.quit()

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
message = client.messages.create(body=msg, from_=TWILIO_NUMBER, to=MY_NUMBER)
