import os
import datetime

import requests
import vk_api
from vk_api.upload import VkUpload
from loguru import logger

from timer import Timer

CAT_URL = 'https://source.unsplash.com/featured/?cat'
WHEN_TO_CALL = datetime.time(0, 0, 0)
TOKEN = os.getenv('VK_TOKEN')
STANDARD_FILE_NAME = 'cat.jpeg'


logger.add('catpick.log')


class Vk:
    def __init__(self, token):
        self.vk = vk_api.VkApi(token=token)
        self.api = self.vk.get_api()

    def upload_avatar(self, f_name):
        upload = VkUpload(self.vk)
        with open(f_name, 'rb') as f:
            resp = upload.photo_profile(f)
            logger.info(resp)

    def get_old_photo_id(self):
        resp = self.vk.method('photos.get', {'album_id': '-6'})
        logger.info(resp)

        if resp['count'] < 2:
            return

        photo_id = None
        mn_date = 10000000000

        for e in resp['items']:
            if e['date'] < mn_date:
                mn_date = e['date']
                photo_id = e['id']

        return photo_id

    def delete_old_photo(self):
        old_photo_id = self.get_old_photo_id()
        if not old_photo_id:
            return

        resp = self.vk.method('photos.delete', {'photo_id': old_photo_id})
        logger.info(resp)

    def get_last_post(self):
        wall = self.vk.method('wall.get')
        logger.info(wall)

        if wall['count'] == 0:
            return

        post_id = wall['items'][0]['id']
        return post_id

    def delete_last_post(self):
        post_id = self.get_last_post()
        if not post_id:
            return

        resp = self.vk.method('wall.delete', {'post_id': post_id})
        logger.info(resp)


def get_new_cat(f_name):
    resp = requests.get(CAT_URL)
    with open(f_name, 'wb') as f:
        f.write(resp.content)


@logger.catch
def process():
    get_new_cat(STANDARD_FILE_NAME)

    vk = Vk(TOKEN)

    vk.upload_avatar(STANDARD_FILE_NAME)
    vk.delete_old_photo()
    vk.delete_last_post()


if __name__ == '__main__':
    # process()
    t = Timer(process)
    t.call_everyday((WHEN_TO_CALL,))
    t.run()
