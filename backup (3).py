import json
from datetime import datetime
from pprint import pprint
from typing import Any

import requests
from tqdm import tqdm

from configuration import config  # Импорт доступа к VK API


class Vkontakte:
    def __init__(
            self, vkontakte_token: str, vkontakte_id: int,
            version: str = "5.236", count: int = 5):
        self.token = vkontakte_token  # Инициализация токена VK
        self.id = vkontakte_id  # Инициализация ID пользователя VK
        self.version = version  # Инициализация версии API VK
        self.count = count  # Инициализация количества фотографий
        self.params = {"access_token": self.token, "v": self.version}

    def vk_response(self):  # получениt информации о фотографиях VK
        params: dict[str, Any] = {"owner_id": self.id,
                                  "album_id": "profile",
                                  "rev": 0,
                                  "extended": 1,
                                  "photo_sizes": 1,
                                  "count": self.count}

        response: requests.models.Response = requests.get(
            url="https://api.vk.com/method/photos.get",
            params={**self.params, **params})  # Выполнение запроса к VK API

        if response.status_code == 200:  # Проверка статуса запроса
            data = response.json()  # Преобразование ответа в JSON формат
            photos: list = data["response"]["items"]  # список фото
            photos_infos: dict = {}  # словарь для хранения фото
            for photo in photos:
                photo_likes: int = photo["likes"]["count"]
                photo_date: str = datetime.fromtimestamp(
                    photo["date"]).strftime('%Y_%m_%d_%H_%M_%S')
                photo_sizes: list = sorted(
                    photo["sizes"], key=lambda x: x["height"] * x["width"])
                photo_url: str = photo_sizes[-1]["url"]
                size_type: str = photo_sizes[-1]["type"]

                photo_info = {"url": photo_url,
                              "likes": photo_likes,
                              "date": photo_date,
                              "size_type": size_type}

                if photo_likes not in photos_infos:
                    photos_infos[photo_likes] = photo_info
                else:
                    photos_infos[f"{photo_likes}_{photo_date}"] = photo_info

            return photos_infos
        else:
            print(
                f"Ошибка запроса. Код состояния HTTP: {response.status_code}")

    def save_to_json(self):
        filename = f"{self.id}.json"  # имя файла для сохранения информации
        data = self.vk_response()
        data_dump = []

        for key, value in data.items():
            data_dump.append(
                {"file_name": f"{key}.jpg", "size": value["size_type"]})

        with open(filename, 'w', encoding='utf-8') as json_file:
            json.dump(data_dump, json_file, ensure_ascii=False, indent=4)


class YandexDisk:  # Объявление класса YandexDisk для работы с YandexDisk API
    def __init__(self, yandex_token: str):
        self.token = yandex_token
        self.headers = {"Content-Type": "application/json",
                        "Authorization": f"OAuth {yandex_token}"}

    def create_folder(self, folder_name: str) -> str:
        url: str = "https://cloud-api.yandex.net/v1/disk/resources"
        params: dict[str, str] = {"path": folder_name}

        response = requests.get(url, headers=self.headers, params=params)
        response_data = response.json()
        response_status = response.status_code

        if response_status != 200:
            if response_status == 404:
                print(f"Папка {folder_name} отсутствует!")
            else:
                print(f"Статус запроса: {response_status}\n"
                      f"Описание: {response_data['message']}")

            response = requests.put(url, headers=self.headers, params=params)
            response_status = response.status_code

            if response_status in [200, 201]:
                print(f'Папка {folder_name} успешно создана!')
                return folder_name
            else:
                print(f"Статус запроса: {response_status}\n"
                      f"Описание: {response_data['message']}")
                return "Папка не создана!"
        else:
            print(f'Папка {folder_name} уже существует')
            return folder_name

    def files_in_folder(self, folder_name: str):
        url = "https://cloud-api.yandex.net/v1/disk/resources"
        params = {'path': folder_name}
        response = requests.get(url, headers=self.headers, params=params)
        response_status = response.status_code

        if response_status == 200:
            data = response.json()['_embedded']['items']
            files = []
            for item in data:
                files.append(item['name'])
            return files
        else:
            return None

    def upload_photos(self, folder_name: str):
        """
        Загрузка фото на Я.Диск.
        """
        folder: str = ya.create_folder(folder_name)
        files: str = ya.files_in_folder(folder_name)
        if folder == folder_name:
            photos_dict: dict = vk.vk_response()

            for key, value in tqdm(photos_dict.items()):
                if f"{key}.jpg" not in files:
                    params: dict[str, Any] = {"path": f"{folder}/{key}.jpg",
                                              "url": value["url"],
                                              "overwrite": False}
                    response = requests.post(
                        url="https://cloud-api.yandex.net/v1/disk/resources/upload",
                        headers=self.headers,
                        params=params)
                    response_data = response.json()
                    response_status = response.status_code

                    if response_status not in [200, 202]:
                        print(f"Статус запроса: {response_status}\n"
                              f"Описание: {response_data['message']}")
                else:
                    print(f"Файл {key} уже существует")

            print("BackUp успешно выполнен!")


if __name__ == "__main__":
    # Исходные данные:
    ya_token = config.ya_token.get_secret_value()
    vk_token = config.vk_token.get_secret_value()
    vk_id = config.vk_id.get_secret_value()
    # Экземпляры классов:
    vk: Vkontakte = Vkontakte(vkontakte_token=vk_token, vkontakte_id=vk_id)
    ya: YandexDisk = YandexDisk(yandex_token=ya_token)

    print_info = True  # Флаг вывода информации

    if print_info:
        pprint(vk.vk_response())
    else:
        pass  # Вывод информации о фотографиях в консоль

    vk.save_to_json()  # Сохранение информации о фотографиях в JSON файл
    ya.upload_photos(folder_name="VKBackupLessons")
