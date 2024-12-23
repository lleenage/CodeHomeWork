from dotenv import load_dotenv
import os.path
import requests
from pprint import pprint
import json

from tqdm.notebook import trange
from time import sleep
from tqdm import trange, tqdm

dotenv_path = "confirm.env"
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

vk_acces_token = os.getenv("VK_TOKEN")
ya_token = os.getenv("YA_TOKEN")
user_id = "821271818"


class VKontacte:
    def __init__(self, acces_token, version="5.131"):
        self.version = version
        self.token = acces_token
        self.base_url = "https://api.vk.com/method/"
        self.params = {"access_token": self.token, "v": self.version}

    def photo_info(self, user_ids, count=5):
        url = f"{self.base_url}photos.get"
        param = {
            **self.params,
            "owner_id": user_ids,
            "album_id": "profile",
            "count": count,
            "extended": 1,
        }
        response = requests.get(url, params=param)
        return response.json()

    def biggest_photo(self, user_ids, count=5):
        url = f"{self.base_url}photos.get"
        param = {
            **self.params,
            "owner_id": user_ids,
            "album_id": "profile",
            "count": count,
        }
        response = requests.get(url, params=param)
        photo = response.json()
        photo_inf = []
        for ph in photo["response"]["items"]:
            photo_inf.append(ph["sizes"])
            biggest_photos = []
            for inf in photo_inf:
                for i in inf:
                    if i["type"] == "z":
                        biggest_photos.append(i["url"])
        return biggest_photos


class Yandex:
    def __init__(self, token):
        self.headers = {"Authorization": f"OAuth {token}"}

    def create_folder(self, folder_name):
        response = requests.put(
            url="https://cloud-api.yandex.net/v1/disk/resources",
            headers=self.headers,
            params={"path": folder_name},
        )
        return response.status_code

    def upload_photo(self, photo_url, photo_info):
        all_photo = []
        for j, i in zip(
            photo_info["response"]["items"],
            tqdm(photo_url, desc="Общая загрузка всех фотографий"),
        ):
            photo_name = j["likes"]["count"]
            url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
            param = {"path": f"/photo/{photo_name}.jpg", "url": i}
            headers = self.headers
            response = requests.post(url, params=param, headers=headers)
            sleep(0.01)
            for x in trange(10000, desc=f'Загрузка фотографии "{photo_name}"'):
                sleep(0.0001)
            all_photo.append(response)

            with open("result.json", "w", encoding="utf-8") as file:
                res = []
                for i in photo_info:
                    dict_res = {}
                    dict_res["file_name"] = f"{photo_name}.jpg"
                    dict_res["size"] = "z"
                    res.append(dict_res)
                json.dump(res, file)

        return all_photo


vk_user = VKontacte(vk_acces_token)
yandex = Yandex(ya_token)

photo_info = vk_user.photo_info(user_id)
photo_url = vk_user.biggest_photo(user_id)
# pprint(photo_url)
# pprint(photo_info)
# print(yandex.create_folder('photo'))
yandex.upload_photo(photo_url, photo_info)
# pprint(yandex.upload_photo(photo_url, photo_info))
