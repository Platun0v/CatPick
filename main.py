import os
import random
from typing import List

import requests
import vk_api
from vk_api.upload import VkUpload
from telethon.sync import TelegramClient, functions
from loguru import logger

import config

logger.add(config.LOG_FILE)


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


class Tg:
    def __init__(self, session_name='CatPick'):
        self.client = TelegramClient(session_name, config.API_ID, config.API_HASH)
        self.client.connect()

    def get_last_photo(self):  # 1921618168832436147
        result = self.client(functions.photos.GetUserPhotosRequest(
            user_id='platun0v',
            offset=0,
            max_id=0,
            limit=100
        )).photos[0]
        logger.info(result)
        return result

    def delete_old_photo(self):
        photo = self.get_last_photo()
        result = self.client(functions.photos.DeletePhotosRequest(id=[photo]))
        logger.info(result)

    def upload_avatar(self, f_name: str):
        result = self.client(functions.photos.UploadProfilePhotoRequest(file=self.client.upload_file(f_name)))
        logger.info(result)


def get_new_cat(f_name):
    dir_file = check_dir(config.IMGS_DIR)
    if dir_file:
        mv_img(f'{config.IMGS_DIR}/{dir_file}', f_name)
        return
    resp = requests.get(config.UNSPLASH_URL)
    with open(f_name, 'wb') as f:
        f.write(resp.content)


def check_dir(imgs_dir: str) -> str:
    if not os.path.exists(imgs_dir):
        os.mkdir(imgs_dir)

    files = os.listdir(imgs_dir)
    if files:
        return random.choice(files)
    return ''


def mv_img(old_file: str, new_file: str):
    os.remove(new_file)
    os.rename(old_file, new_file)


@logger.catch
def process():
    get_new_cat(config.STANDARD_FILE_NAME)

    vk = Vk(config.TOKEN)

    vk.upload_avatar(config.STANDARD_FILE_NAME)
    vk.delete_old_photo()
    vk.delete_last_post()

    tg = Tg(config.SESSION_FILE)

    tg.delete_old_photo()
    tg.upload_avatar(config.STANDARD_FILE_NAME)


if __name__ == '__main__':
    process()
