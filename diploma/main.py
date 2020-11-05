import os
from params import *
import requests
from datetime import datetime
import json
import shutil
from tqdm import tqdm
from API.YandexAPI import YaDiskAPI
from API.VKAPI import VKAPI


class App():
    """Main application class
    Application orchestration logic
    """

    DBG = True
    PHOTO_FOLDER = "VK_Photos"
    PHOTO_COUNT = 3

    def __init__(self):
        self.log("Start")
        self._ya = YaDiskAPI(token=YA_TOKEN,
                             root_folder=ROOT_YA_FOLDER,
                             debug=self.DBG)
        self._vk = VKAPI(token=VK_TOKENT,
                         debug=self.DBG)

    def log(self, message):
        if self.DBG:
            print(f"MAIN: {datetime.now()}: {message}")

    def run(self):
        self.log("Start")
        input_user_id = input("Введите имя или ID пользователя VK: ")
        if input_user_id == "":
            self.log("Введен пустой ID. Запрашиваем по токену")
            input_user_id = None
        elif not input_user_id.isdigit():
            self.log(f"Введено имя пользователя {input_user_id}. Запрос ID.")
            input_user_id = self._vk.get_user_info(input_user_id)["id"]
            self.log(f"Id: {input_user_id}")
        else:
            self.log(f"Введен ID: {input_user_id}")
        self.log("Create backup folder")
        self._ya.create_folder(VK_FOLDER)
        self.create_photos_folder()
        photos = self._vk.get_photos(input_user_id)
        photos = self.process_vk_photos(photos)
        print(photos)
        # Download files to folder
        photo_folder = os.path.join(os.getcwd(), self.PHOTO_FOLDER)
        res = []
        cur_date = datetime.now().strftime("%d_%m_%YT%H%M%S")
        print(cur_date)
        for photo in photos:
            # generate file name
            photo_path = os.path.join(photo_folder, photo["likes"])
            counter = 0
            while os.path.isfile(photo_path + ".jpg"):
                counter += 1
                photo_path += f"_{str(counter)}_{cur_date}"
            # Add photo info to JSON
            res.append({
                "file_name": os.path.basename(photo_path) + ".jpg",
                "size": photo["photo"]["type"]
            })
            # download photo
            with open(photo_path + ".jpg", "wb") as f:
                resp = requests.get(photo["photo"]["url"], stream=True)
                # print(f"donwload {photo['photo']['url']}. Status: {resp.status_code}")
                f.write(resp.content)
        # upload files to yandex
        for cur_file in tqdm(os.listdir(photo_folder)):
            print(f"uploading file {cur_file} to yandex")
            self._ya.upload(file_path=os.path.join(photo_folder, cur_file),
                            dest_folder=VK_FOLDER)
        self.log("Upload JSON to yandex")
        # upload json result
        with open("res.json", "w") as f:
            json.dump(res, f)
        self._ya.upload(file_path="res.json", dest_folder=VK_FOLDER)

        self.log("Done")

    def process_vk_photos(self, photos):
        """Processing raw reaponse from vk
        Get largest url, generate file name
        Arguments:
            photos {[type]} -- [description]
        """
        self.log("Start photo processing.")
        result = []
        for photo in photos:
            max_photo = sorted(photo["sizes"], reverse=True,
                               key=lambda x: x["height"])[0]
            result.append({
                "id": photo["id"],
                "likes": str(photo["likes"]["count"] if "likes" in photo.keys() else None),
                "photo": max_photo
            })
        return result

    def create_photos_folder(self):
        # Remove old folder if exists
        folder_path = os.path.join(os.getcwd(), self.PHOTO_FOLDER)
        if os.path.isdir(folder_path):
            self.log(f"Remove existing folder: {folder_path}")
            shutil.rmtree(folder_path)
            # os.removedirs(folder_path)
        self.log(f"Create folder: {folder_path}")
        os.mkdir(folder_path)


def main():
    app = App()
    app.run()


if __name__ == '__main__':
    main()
