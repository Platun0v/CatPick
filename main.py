import os
import datetime

import requests
import vk_api
from vk_api.upload import VkUpload

from timer import Timer

CAT_URL = 'https://source.unsplash.com/featured/?cat'
WHEN_TO_CALL = datetime.time(0, 0, 0)
TOKEN = os.getenv('VK_TOKEN')


def get_new_cat():
    resp = requests.get(CAT_URL)
    with open('cat.jpeg', 'wb') as f:
        f.write(resp.content)


def update_cat():
    api = vk_api.VkApi(token=TOKEN)
    upload = VkUpload(api)
    with open('cat.jpeg', 'rb') as f:
        resp = upload.photo_profile(f)

    print(resp)


def process():
    get_new_cat()
    update_cat()


if __name__ == '__main__':
    t = Timer(process)
    t.call_everyday((WHEN_TO_CALL,))
    t.run()
