
import os
from dotenv import load_dotenv
from telebot import TeleBot

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

bot = TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Nova is online. 🌒")

def send_alert(content):
    try:
        bot.send_message(TELEGRAM_CHAT_ID, f"🚨 Nova Alert:\n{content}")
        print("✅ Telegram alert sent!")
    except Exception as e:
        print("❌ Telegram alert failed:", e)

if __name__ == "__main__":
    print("📡 Nova Telegram Bot is running.")
    send_alert("Test alert from Nova bot.")
    bot.polling()
