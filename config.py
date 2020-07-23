from dotenv import load_dotenv
load_dotenv()

import os

AVATAR_PICTURE = 'cat'  # Укажите, что бы вы хотели видеть на аватарке

UNSPLASH_URL = f'https://source.unsplash.com/featured/?{AVATAR_PICTURE}'
# За другими вариантами рандомного изображения можно сходить сюда https://source.unsplash.com/

TOKEN = os.getenv('VK_TOKEN')
STANDARD_FILE_NAME = 'img.jpeg'
