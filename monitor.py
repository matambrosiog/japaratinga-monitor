import os
from telegram import Bot

print("Iniciando script...")

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

print("TOKEN:", TOKEN)
print("CHAT_ID:", CHAT_ID)

bot = Bot(token=TOKEN)

bot.send_message(
    chat_id=CHAT_ID,
    text="🚀 TESTE DIRETO DO GITHUB ACTIONS"
)

print("Mensagem enviada com sucesso.")
