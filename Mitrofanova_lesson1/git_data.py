# 1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя,
# сохранить JSON-вывод в файле *.json.

import requests
import json
from utils import f_path


def get_response(url, **kwargs):
    try:
        if kwargs.get('json') is not None:
            return requests.get(url).json()
        else:
            return requests.get(url).text
    except Exception:
        return None


# логин пользователя
username = 'willnight'
# поля которые хотим выводить в итоге
fields_repos = ['id', 'name', 'git_url', 'private']
fields_user = ['id', 'name', 'login', 'url']

response_user = get_response(f'https://api.github.com/users/{username}', json=1)
response_repos = get_response(f'https://api.github.com/users/{username}/repos', json=1)

for i, el in enumerate(response_repos):
    response_repos[i] = {k: v for k, v in el.items() if fields_repos.__contains__(k)}

response_user = {k: v for k, v in response_user.items() if fields_user.__contains__(k)}
response_user['repos'] = response_repos

with open(f'{f_path}git_repos.json', 'w') as f:
    f.write(json.dumps(response_user, indent=4, sort_keys=True, ensure_ascii=False))
