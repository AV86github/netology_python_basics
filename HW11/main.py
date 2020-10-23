from params.example import *
from urllib.parse import urljoin
import requests


class VKApi():
    VK_API = "https://api.vk.com/method/"
    VERSION = "5.124"

    def __init__(self, token=None, token_owner_id=None, debug=False):
        self._token = token
        self._params = {
            "access_token": token,
            "v": self.VERSION
        }
        self._dbg = debug
        if self._dbg:
            print("Init params: ", self._params)
        if not token_owner_id:
            token_owner_id = self._get_info_by_token(token)
        self._token_owner_id = token_owner_id

    def get_friends(self, user_id=None):
        """reutrn friends for given user
        if user_id is None - return friends for current token
        VK API Method: friends.get
        Keyword Arguments:
            user_id {str} -- [description] (default: {None})
        """
        if self._dbg:
            print("Start get_friends func")
        if not user_id:
            user_id = self._token_owner_id
        method = "friends.get"
        cust_params = self._params.copy()
        cust_params.update({
            "user_id": user_id
        })
        friends = self._send_request(method, cust_params)["response"]["items"]
        if self._dbg:
            print("get_friends method return: ", friends)
        return friends

    def get_user_info(self, user_id=None):
        """return info about account
        
        [description]
        
        Keyword Arguments:
            user_id {[str]} -- [description] (default: {None})
        """
        if self._dbg:
            print("Start get_user_info func")
        if not user_id:
            user_id = self._token_owner_id
        method = "users.get"
        cust_params = self._params.copy()
        cust_params.update({
            "user_ids": user_id
        })
        info = self._send_request(method, cust_params)["response"][0]
        if self._dbg:
            print("get_user_info method return: ", info)
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
        return self._send_request(method, self._params)["response"][0]["id"]

    def _send_request(self, method, params):
        print(f"Invoke method: {method}")
        if self._token is None:
            print("Offline.")
            return {
                "response": ["Dummy"]
            }
        if self._dbg:
            print(f"{method} params: ", params)
        url = urljoin(self.VK_API, method)
        response = requests.get(url,
                                params=params,
                                timeout=(10, 10))
        if self._dbg:
            print("Response: ", response.json())
        return response.json()


class VKUser():
    """docstring for VKUser"""
    VK_PROFIE_URL = "https://vk.com/id"

    def __init__(self, user_id, api=None):
        self._user_id = user_id
        if api is None:
            api = VKApi(token=TOKEN)
        self._api = api

    def __str__(self):
        return self.VK_PROFIE_URL + self._user_id

    def __and__(self, other):
        print("Get shared friends")
        self_friends = set(self.get_friends())
        other_friends = set(other.get_friends())
        shared_friends = self_friends & other_friends
        return [VKUser(x, api=self._api) for x in shared_friends]

    def get_info(self):
        return self._api.get_user_info(user_id=self._user_id)

    def get_friends(self):
        return self._api.get_friends(user_id=self._user_id)


def main():
    api = VKApi(token=TOKEN, debug=True)
    api.get_user_info()

    user1 = VKUser("552934290")
    user2 = VKUser("552934290")
    user1 & user2


if __name__ == '__main__':
    main()
