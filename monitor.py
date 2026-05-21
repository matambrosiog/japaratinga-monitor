from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

import requests
import time
import re
import os

URL = "SEU_LINK_DA_OMNIBEES"


TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

driver.get(URL)

time.sleep(10)

texto = driver.page_source

driver.quit()

precos = re.findall(r'R\\$\\s?[\\d\\.]+,\\d{2}', texto)

if precos:
    menor_preco = precos[0]

    mensagem = f"""
🏨 Japaratinga Monitor

💰 Menor preço encontrado:
{menor_preco}

🔗 {URL}
"""

    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": mensagem
        }
    )

    print("Mensagem enviada!")
else:
    print("Preço não encontrado")
