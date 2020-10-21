import requests

from params import *


global hero_list
hero_name_list = ["Hulk",
                  "Captain America",
                  "Thanos"]


def get_hero_info(hero_name):
    return requests.get(f"{API_URL}{AUTH_TOKEN}/search/{hero_name}",
                        timeout=(10, 10)).json()


def get_smartest_hero(hero_dict):
    """return smartest hero

    [description]

    Arguments:
        hero_dict - dict of heroes stats. Name: {stat: value, ....}
    """
    if not hero_dict:
        return None
    return sorted(hero_dict.items(), key=lambda x: int(x[1]["intelligence"]),
                  reverse=True)[0][0]


def main():
    hero_stats = {}
    for hero in hero_name_list:
        if hero in hero_stats.keys():
            continue
        print(f"Getting data for {hero}")
        hero_data = get_hero_info(hero)
        if hero_data["response"] == "success":
            hero_stats.setdefault(hero, hero_data["results"][0]["powerstats"])
    print("Smartest:", get_smartest_hero(hero_stats))


if __name__ == '__main__':
    main()
