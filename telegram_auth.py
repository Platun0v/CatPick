from telethon import TelegramClient
import config

session_name = 'CatPick'

client = TelegramClient(session_name, config.API_ID, config.API_HASH)
client.start()
