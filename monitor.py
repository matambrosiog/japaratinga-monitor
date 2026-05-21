import os
import re
import json
import time

from telegram import Bot

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
PRICE_ALERT = float(os.getenv("PRICE_ALERT", 8000))

URL = "https://book.omnibees.com/hotelresults?c=5173&q=8259&currencyId=16&lang=pt-BR&hotel_folder=&NRooms=1&age=&group_code=&Code=&loyalty_code=&ag=&submited=false&CheckIn=11102027&CheckOut=17102027&CheckIn_formated=11%2F10%2F2027&CheckIn_formated_submit=11%2F10%2F27&CheckOut_formated=17%2F10%2F2027&CheckOut_formated_submit=17%2F10%2F27&ad=2&ch=0&ag1=1&ag2=1&_gl=1*4zpr4l*_gcl_au*MTQwNDg0NTY4NC4xNzc5MzIyMDEw*_ga*MjAwNzAxNzY3LjE3NzkzMjIwMTE.*_ga_H3RJ7JE8EV*czE3NzkzMjIwMTEkbzEkZzEkdDE3NzkzMjIwNTAkajMwJGwwJGgxMDE3ODI2MDY3"
HOTEL_NAME = "Japaratinga Lounge Resort"

bot = Bot(token=TOKEN)

HISTORY_FILE = "prices.json"


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return {}

    with open(HISTORY_FILE, "r") as f:
        return json.load(f)


def save_history(data):
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f)


def extract_price(text):
    prices = re.findall(r"R\\$\\s?([\\d\\.]+,\\d{2})", text)

    if not prices:
        return None

    values = []

    for p in prices:
        value = p.replace(".", "").replace(",", ".")
        values.append(float(value))

    return min(values)


def send_telegram(message):
    bot.send_message(chat_id=CHAT_ID, text=message)


def check_price():

    print("Abrindo navegador...")

    chrome_options = Options()

    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=chrome_options)

    driver.get(URL)

    time.sleep(10)

    page_text = driver.page_source

    driver.quit()

    price = extract_price(page_text)

    if not price:
        print("Preço não encontrado.")
        return

    print(f"Preço encontrado: R$ {price}")

    history = load_history()

    last_price = history.get("last_price")

    should_alert = False

    if last_price:
        if price < last_price:
            should_alert = True

    if price <= PRICE_ALERT:
        should_alert = True

    if should_alert:

        difference = ""

        if last_price:
            diff = last_price - price

            if diff > 0:
                difference = f"\\nEconomia: R$ {diff:.2f}"

        message = f'''
🔥 PREÇO ENCONTRADO

🏨 {HOTEL_NAME}

📅 11/10/2027 → 17/10/2027

💰 Atual: R$ {price:.2f}

📉 Anterior: {last_price if last_price else "Sem histórico"}
{difference}

🌐 {URL}
'''

        send_telegram(message)

        print("Alerta enviado.")

    history["last_price"] = price

    save_history(history)


if __name__ == "__main__":
    check_price()
