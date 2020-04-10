import sys

import requests


def get_info(to_do):
    to_do = to_do.replace(" ", "+")
    response = requests.get(
        url="http://geocode-maps.yandex.ru/1.x/",
        params={
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": to_do,
            "format": "json"
        }
    )
    if not response:
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)
    json_obj = response.json()
    dad = json_obj["response"]["GeoObjectCollection"]["featureMember"][0]['GeoObject']
    ans = {
        'address': dad['metaDataProperty']['GeocoderMetaData']['text'],
        'coord': dad["Point"]["pos"].replace(" ", ","),
        'postcode': '-'
    }
    try:
        ans['postcode'] = dad["metaDataProperty"]["GeocoderMetaData"]["Address"]['postal_code']
    except BaseException as exc:
        pass
    return ans


def take_photo(dest, map_params):
    response = requests.get(
        url="http://static-maps.yandex.ru/1.x/",
        params=map_params
    )
    if not response:
        print("Http статус:", response.status_code, "(", response.reason, ")")
        sys.exit(1)
    with open(dest, "wb") as file:
        file.write(response.content)
