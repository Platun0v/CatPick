import requests
import vk_api
from vk_api.upload import VkUpload
import os

CAT_URL = 'https://source.unsplash.com/featured/?cat'
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


if __name__ == '__main__':
    get_new_cat()
    update_cat()
