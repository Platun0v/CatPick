from dotenv import load_dotenv

load_dotenv()

import os

AVATAR_PICTURE = 'cat'  # Укажите, что бы вы хотели видеть на аватарке

UNSPLASH_URL = f'https://source.unsplash.com/featured/?{AVATAR_PICTURE}'
# За другими вариантами рандомного изображения можно сходить сюда https://source.unsplash.com/

TOKEN = os.getenv('VK_TOKEN')
API_ID = os.getenv('TG_API_ID')
API_HASH = os.getenv('TG_API_HASH')

STANDARD_FILE_NAME = 'img.jpeg'
IMGS_DIR = 'imgs'
LOG_FILE = os.getenv('LOG_FILE', 'catpick.log')
SESSION_FILE = os.getenv('SESSION_FILE', 'CatPick.session')
