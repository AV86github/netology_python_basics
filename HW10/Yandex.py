import requests

from params.example import *
import os


class YaUploader:
    def __init__(self, token: str):
        self.token = token
        self._headers = {
            "Authorization": f"OAuth {token}"
        }
        self._root_folders = []
        self._create_netology_folder()

    def _create_netology_folder(self):
        if not self._root_folders:
            self._root_folders = self._get_folder_list("/")
        if "netology" not in self._root_folders:
            print("Creating netology folder...")
            self._create_folder("/netology")

    def _create_folder(self, folder_path):
        status = requests.put(f"{YANDEX_API}/resources",
                              headers=self._headers,
                              params={
                                "path": folder_path
                              })
        print("Done. Status:", status.status_code)

    def _get_folder_list(self, root_path):
        params = {
            "path": "/",
            "offset": 1
        }
        folder = requests.get(f"{YANDEX_API}/resources",
                              headers=self._headers,
                              params=params)
        return [x["name"] for x in folder.json()["_embedded"]["items"]]

    def _get_url_for_upload(self, file_name):
        params = {
            "path": f"/netology/{file_name}",
            "overwrite": "true"
        }
        return requests.get(f"{YANDEX_API}/resources/upload",
                            headers=self._headers,
                            params=params)

    def upload(self, file_path: str):
        """Метод загруджает файл file_path на яндекс диск"""
        response = self._get_url_for_upload(os.path.basename(file_path))
        if response.status_code // 100 != 2:
            print("Failed to upload file. Error in 1 step.")
            return response.status_code
        else:
            href = response.json()["href"]
            print(href)
            with open(file_path, "rb") as f:
                status = requests.put(href, files={"file": f})
            return status.status_code


if __name__ == '__main__':
    uploader = YaUploader(YANDEX_TOKEN)
    result = uploader.upload("test.file")
