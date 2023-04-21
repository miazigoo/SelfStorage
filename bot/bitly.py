from urllib.parse import urlparse

import requests


def count_clicks(url, token):
    request_url = f'https://api-ssl.bitly.com/v4/bitlinks/{url}/clicks/summary'

    headers = {
        'Authorization': token,
    }

    params = {
        ('unit', 'day'),
        ('units', '-1'),
    }

    response = requests.get(request_url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()['total_clicks']


def is_bitlink(url, token):
    request_url = f'https://api-ssl.bitly.com/v4/bitlinks/{url}'

    headers = {
        'Authorization': token,
    }

    response = requests.get(request_url, headers=headers)
    return response.ok


def get_clicks(url, token):
    parsed_url = urlparse(url)
    cropped_url = "".join([parsed_url.netloc, parsed_url.path])

    if is_bitlink(cropped_url, token):
        return f"По Вашей ссылке прошли: {count_clicks(cropped_url, token)} раз(а)"
    else:
        return f"Введенная ссылка не является ссылкой битлинк"

if __name__ == "__main__":
   pass