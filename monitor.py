from selenium import webdriver
from selenium.webdriver.common.by import By
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

# espera carregar os quartos/preços
time.sleep(15)

print("Capturando preços...")

# pega todos os elementos contendo R$
elementos = driver.find_elements(By.XPATH, "//*[contains(text(),'R$')]")

valores = []

for elemento in elementos:

    texto = elemento.text.strip()

    print(texto)

    match = re.search(r'R\$\s?([\d\.]+,\d{2})', texto)

    if match:

        valor_str = match.group(1)

        valor_float = float(
            valor_str.replace('.', '').replace(',', '.')
        )

        # ignora valores pequenos/filtros laterais
        if valor_float > 10000:
            valores.append(valor_float)

driver.quit()

print("Valores encontrados:")
print(valores)

if valores:

    menor = min(valores)

    valor_formatado = f"R$ {menor:,.2f}" \
        .replace(",", "X") \
        .replace(".", ",") \
        .replace("X", ".")

    mensagem = f"""
🏨 Japaratinga Monitor

💰 Menor preço encontrado:
{valor_formatado}

📅 11/10/2027 → 17/10/2027

🔗 {URL}
"""

    response = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": mensagem
        }
    )

    print("Mensagem enviada!")
    print(response.text)

else:

    print("Nenhum preço válido encontrado")

    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        data={
            "chat_id": CHAT_ID,
            "text": "⚠️ Nenhum preço encontrado no monitor do Japaratinga."
        }
    )
