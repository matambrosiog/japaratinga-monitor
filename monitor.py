from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import requests
import time
import re
import os

URL = "https://book.omnibees.com/hotelresults?c=5173&q=8259&currencyId=16&lang=pt-BR&hotel_folder=&NRooms=1&age=&group_code=&Code=&loyalty_code=&ag=&submited=false&CheckIn=11102027&CheckOut=17102027&CheckIn_formated=11%2F10%2F2027&CheckIn_formated_submit=11%2F10%2F27&CheckOut_formated=17%2F10%2F2027&CheckOut_formated_submit=17%2F10%2F27&ad=2&ch=0&ag1=1&ag2=1"

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

options = Options()

options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

print("Abrindo página...")

driver.get(URL)

time.sleep(15)

html = driver.page_source

driver.quit()

print("Página carregada")

precos = re.findall(r'R\$\s?[\d\.]+,\d{2}', html)

print(precos)

if precos:
    menor_preco = precos[0]

    mensagem = f"""
🏨 Japaratinga Monitor

💰 Preço encontrado:
{menor_preco}

🔗 {URL}
"""

    response = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": mensagem
        }
    )

    print(response.text)

else:
    print("Nenhum preço encontrado")
