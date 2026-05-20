import os
import re
import sqlite3
import time
import schedule

from dotenv import load_dotenv
from telegram import Bot
from playwright.sync_api import sync_playwright

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
PRICE_ALERT = float(os.getenv("PRICE_ALERT", 8000))

bot = Bot(token=TOKEN)

DB_NAME = "prices.db"

CHECKIN = "11/10/2027"
CHECKOUT = "17/10/2027"

HOTEL_NAME = "Japaratinga Lounge Resort"
URL = "https://www.japaratingaresort.com.br/"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            price REAL
        )
        """
    )

    conn.commit()
    conn.close()



def save_price(price):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO prices (date, price) VALUES (datetime('now'), ?)",
        (price,),
    )

    conn.commit()
    conn.close()



def get_last_price():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT price FROM prices ORDER BY id DESC LIMIT 1"
    )

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None


def send_telegram(message):
    try:
        bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")


def check_price():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(URL)

            page.fill('input[placeholder="Check-in"]', CHECKIN)
            page.fill('input[placeholder="Check-out"]', CHECKOUT)
            page.click('button:has-text("Buscar")')

            page.wait_for_selector(".preco", timeout=10000)

            price_text = page.locator(".preco").first.text_content()
            price = float(re.sub(r"[^\d,]", "", price_text).replace(",", "."))

            browser.close()

            print(f"Preço encontrado: R$ {price}")
            save_price(price)

            last_price = get_last_price()
            if last_price and last_price < PRICE_ALERT:
                message = f"🚨 Alerta de preço!\n{HOTEL_NAME}\nPreço: R$ {price}\nData: Check-in {CHECKIN} - Check-out {CHECKOUT}"
                send_telegram(message)

                print("Alerta enviado.")

            else:
                print("Nenhuma queda relevante.")

    except Exception as e:
        print(f"Erro ao verificar preço: {e}")
        error_message = f"❌ Erro no monitor:\n{str(e)}"
        send_telegram(error_message)


if __name__ == "__main__":
    init_db()

    check_price()

    schedule.every(6).hours.do(check_price)

    print("Monitor iniciado...")

    while True:
        schedule.run_pending()
        time.sleep(60)
