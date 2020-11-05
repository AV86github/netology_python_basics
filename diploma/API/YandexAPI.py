import os
import requests
from datetime import datetime


class YaDiskAPI():
    """Yandex dick api
    restricted for netology root folder
    """

    YANDEX_API = "https://cloud-api.yandex.net/v1/disk"

    def __init__(self, token: str, root_folder: str, debug=False):
        self.token = token
        self._root_ya_folder = root_folder
        self.DBG = debug
        self._headers = {
            "Authorization": f"OAuth {token}"
        }
        self._root_folders = []
        self._create_netology_folder()

    def log(self, message):
        if self.DBG:
            print(f"YAAPI: {datetime.now()}: {message}")

    def _create_netology_folder(self):
        if not self._root_folders:
            self._root_folders = self._get_folder_list("/")
        if self._root_ya_folder not in self._root_folders:
            self.log("Creating netology folder...")
            self.create_folder("")

    def create_folder(self, folder_path):
        """create folder in root folder

        [description]

        Arguments:
            folder_path {[type]} -- [description]
        """
        folder_path = f"/{self._root_ya_folder}/{folder_path}"
        self.log(f"Create folder: {folder_path}")
        status = requests.put(f"{self.YANDEX_API}/resources",
                              headers=self._headers,
                              params={
                                  "path": folder_path
                              })
        if status.status_code == 409:
            self.log(f"Folder {folder_path} allready exists")
        else:
            self.log("Done. Status:" + str(status.status_code))

    def _get_folder_list(self, root_path):
        params = {
            "path": "/",
            "offset": 1
        }
        folder = requests.get(f"{self.YANDEX_API}/resources",
                              headers=self._headers,
                              params=params)
        return [x["name"] for x in folder.json()["_embedded"]["items"]]

    def _get_url_for_upload(self, file_name, dest_folder):
        if not dest_folder.endswith("/"):
            dest_folder += "/"
        params = {
            "path": f"/{self._root_ya_folder}/{dest_folder}{file_name}",
            "overwrite": "true"
        }
        return requests.get(f"{self.YANDEX_API}/resources/upload",
                            headers=self._headers,
                            params=params)

    def upload(self, file_path: str, dest_folder: str, file_name=None):
        """Метод загруджает файл file_path на яндекс диск"""
        if file_name is None:
            file_name = os.path.basename(file_path)
        response = self._get_url_for_upload(file_name, dest_folder)
        if response.status_code // 100 != 2:
            self.log("Failed to upload file. Error in 1 step.")
            return response.status_code
        else:
            href = response.json()["href"]
            self.log(href)
            with open(file_path, "rb") as f:
                status = requests.put(href, files={"file": f})
            return status.status_code
