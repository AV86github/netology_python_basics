import os
from params import *
import requests
from datetime import datetime
from urllib.parse import urljoin
import json
import shutil
from tqdm import tqdm


class App():
    """Main application class
    Application orchestration logic
    """

    DBG = True
    PHOTO_FOLDER = "VK_Photos"
    PHOTO_COUNT = 3

    def __init__(self):
        self.log("Start")
        self._ya = YaDiskAPI(token=YA_TOKEN, debug=self.DBG)
        self._vk = VKAPI(token=VK_TOKENT,
                         debug=self.DBG)

    def log(self, message):
        if self.DBG:
            print(f"MAIN: {datetime.now()}: {message}")

    def run(self):
        self.log("Create backup folder")
        self._ya.create_folder(VK_FOLDER)
        self.create_photos_folder()
        photos = self._vk.get_photos()
        photos = self.process_vk_photos(photos)
        print(photos)
        # Download files to folder
        photo_folder = os.path.join(os.getcwd(), self.PHOTO_FOLDER)
        res = []
        for photo in photos:
            # generate file name
            photo_path = os.path.join(photo_folder, photo["likes"])
            counter = 0
            while os.path.isfile(photo_path + ".jpg"):
                counter += 1
                photo_path += "_" + str(counter)
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


class YaDiskAPI():
    """Yandex dick api
    restricted for netology root folder
    """

    YANDEX_API = "https://cloud-api.yandex.net/v1/disk"

    def __init__(self, token: str, debug=False):
        self.token = token
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
        if ROOT_YA_FOLDER not in self._root_folders:
            self.log("Creating netology folder...")
            self.create_folder("")

    def create_folder(self, folder_path):
        """create folder in root folder

        [description]

        Arguments:
            folder_path {[type]} -- [description]
        """
        folder_path = f"/{ROOT_YA_FOLDER}/{folder_path}"
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
            "path": f"/{ROOT_YA_FOLDER}/{dest_folder}{file_name}",
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


class VKAPI():
    """VK API
    [description]
    """
    VK_API = "https://api.vk.com/method/"
    VERSION = "5.124"

    def __init__(self, token=None, token_owner_id=None, debug=False):
        self._token = token
        self._params = {
            "access_token": token,
            "v": self.VERSION
        }
        self._dbg = debug
        self.log("Init params: " + str(self._params))
        if not token_owner_id:
            token_owner_id = self._get_info_by_token(token)
        self._token_owner_id = token_owner_id

    def log(self, message):
        if self._dbg:
            print(f"VKAPI: {datetime.now()}: {message}")

    def get_friends(self, user_id=None):
        """reutrn friends for given user
        if user_id is None - return friends for current token
        VK API Method: friends.get
        Keyword Arguments:
            user_id {str} -- [description] (default: {None})
        """
        self.log("Start get_friends func")
        if not user_id:
            user_id = self._token_owner_id
        method = "friends.get"
        friends = self._send_request(method, {
            "user_id": user_id
        })["response"]["items"]
        self.log("get_friends method return: " + str(friends))
        return friends

    def get_photos(self, user_id=None):
        """reutrn user photos
        
        [description]
        
        Arguments:
            user_id {[type]} -- [description]
        """
        self.log("Start get_photos method")
        if user_id is None:
            user_id = self._token_owner_id
        method = "photos.get"
        photo_params = {
            "owner_id": self._token_owner_id,
            "extended": 1,
            "album_id": "profile"
        }
        if self._dbg:
            self.log("mock photo pesponse")
            with open("resultd.json", "r") as f:
                photos = json.load(f)
        else:
            photos = self._send_request(method, photo_params)
        # self.log("get_photos done: " + str(photos))
        return photos["response"]["items"] if photos["response"]["count"] > 0 else None

    def get_user_info(self, user_id=None):
        """return info about account
        Keyword Arguments:
            user_id {[str]} -- [description] (default: {None})
        """
        self.log("Start get_user_info func")
        if not user_id:
            user_id = self._token_owner_id
        method = "users.get"
        info = self._send_request(method, {
            "user_ids": user_id
        })["response"][0]
        self.log("get_user_info method return: ", info)
        return info

    def _get_info_by_token(self, token):
        """Get user id by token
        VK API Method: users.get
        [description]

        Arguments:
            token {[type]} -- [description]

        Returns:
            [str] -- [user id]
        """
        method = "users.get"
        return self._send_request(method)["response"][0]["id"]

    def _send_request(self, method, params=None):
        self.log(f"Invoke method: {method}")
        cust_params = self._params.copy()
        if params is not None:
            cust_params.update(params)
        if self._token is None:
            print("Offline.")
            return {
                "response": ["Dummy"]
            }
        self.log(f"{method} params: " + str(cust_params))
        url = urljoin(self.VK_API, method)
        response = requests.get(url,
                                params=cust_params,
                                timeout=(10, 10))
        self.log("Response: " + str(response.json()))
        return response.json()


def main():
    app = App()
    app.run()


if __name__ == '__main__':
    main()
