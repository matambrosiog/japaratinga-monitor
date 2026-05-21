import os
import re
import json
import requests

from telegram import Bot
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

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


def extract_price(html_content):
    """Extrai o preço usando BeautifulSoup"""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Procura por texto contendo "R$" seguido de número
        # Padrão: R$ XX.XXX,XX
        patterns = [
            r"R\$\s([\d\.]+,\d{2})",
        ]
        
        prices = []
        
        # Primeiro tenta encontrar em tags específicas
        for tag in soup.find_all(text=True):
            text = tag.strip()
            if "R$" in text:
                for pattern in patterns:
                    matches = re.findall(pattern, text)
                    if matches:
                        for match in matches:
                            # Converte "16.794,02" em float
                            value_str = match.replace(".", "").replace(",", ".")
                            try:
                                prices.append(float(value_str))
                            except:
                                pass
        
        if prices:
            # Remove preços muito altos (provavelmente são totalizadores)
            prices = [p for p in prices if p < 100000]
            
            if prices:
                min_price = min(prices)
                print(f"✓ Preço extraído com sucesso: R$ {min_price:.2f}")
                print(f"✓ Todos os preços encontrados: {prices}")
                return min_price
        
        print("✗ Nenhum preço encontrado")
        return None
        
    except Exception as e:
        print(f"✗ Erro ao extrair preço: {e}")
        return None


def send_telegram(message):
    bot.send_message(chat_id=CHAT_ID, text=message)


def check_price():
    print("Verificando preço...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        page = browser.new_page()

        page.goto(URL, timeout=120000)

        page.wait_for_timeout(10000)

        content = page.content()

        browser.close()

    price = extract_price(content)

    if not price:
        print("Preço não encontrado.")
        return

    print(f"✓ Preço encontrado: R$ {price:.2f}")

    history = load_history()

    last_price = history.get("last_price")

    # Mensagem com informação do preço atual
    price_message = f'''
📊 CONSULTA DE PREÇO

🏨 {HOTEL_NAME}

📅 11/10/2027 → 17/10/2027

💰 Preço Atual: R$ {price:.2f}

📉 Preço Anterior: {f"R$ {last_price:.2f}" if last_price else "Sem histórico"}

🎯 Preço Alerta: R$ {PRICE_ALERT:.2f}

🌐 Consulta Realizada
'''

    send_telegram(price_message)
    print("✓ Mensagem de preço enviada.")

    # Alerta se preço caiu ou está abaixo do alerta
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
                difference = f"\n💚 Economia: R$ {diff:.2f}"

        alert_message = f'''
🔥 ALERTA DE PREÇO!

🏨 {HOTEL_NAME}

📅 11/10/2027 → 17/10/2027

💰 Preço: R$ {price:.2f}
{difference}

🌐 Consulta Realizada
'''

        send_telegram(alert_message)

        print("✓ Alerta enviado.")

    history["last_price"] = price

    save_history(history)


if __name__ == "__main__":
    check_price()
