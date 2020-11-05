import requests
from datetime import datetime
from urllib.parse import urljoin
import json


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
        self.log("get_user_info method return: " + str(info))
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
