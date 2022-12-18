import os, requests

RSPP_ENDPOINT = 'https://oauth.reddit.com/r/redscarepodprivate'

def get_env_vars():
    return {'client_id': os.environ['CLIENT_ID'],
            'secret_id': os.environ['SECRET_ID'],
            'reddit_user': os.environ['REDDIT_USERNAME'],
            'reddit_pass': os.environ['REDDIT_PASSWORD']}

def get_token(env_vars):
    auth = requests.auth.HTTPBasicAuth(env_vars['client_id'], env_vars['secret_id'])

    data = {'grant_type': 'password',
            'username': env_vars['reddit_user'],
            'password': env_vars['reddit_pass']}

    headers = {'User-Agent': 'rspp/0.1.1'}

    res = requests.post('https://www.reddit.com/api/v1/access_token',
            auth=auth, data=data, headers=headers)

    token = res.json()['access_token']
    headers = {**headers, **{'Authorization': f"bearer {token}"}}

    return headers

if __name__ == "__main__":
    env_vars = get_env_vars()
    headers = get_token(env_vars)

    res = requests.get(f"{RSPP_ENDPOINT}/new", headers=headers)

    posts = res.json()['data']['children']

    for post in posts:
        post_id = post['data']['id']
        author = post['data']['author']
        print(f'Author: {author}')
        res = requests.get(f'{RSPP_ENDPOINT}/comments/{post_id}', headers=headers)
        comments = res.json()[1]['data']['children']

        for comment in comments:
            c_author = comment['data']['author']
            print(f"Commentator: {c_author}")

        print("-----------------------------------------------------------------")
