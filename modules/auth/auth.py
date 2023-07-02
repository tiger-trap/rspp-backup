""" """
import logging
import os
import requests

TOKEN_ENDPOINT = 'https://www.reddit.com/api/v1/access_token'

logger = logging.getLogger(__name__)

def get_env_vars():
    """ """
    return {'client_id': os.environ['CLIENT_ID'],
            'secret_id': os.environ['SECRET_ID'],
            'reddit_user': os.environ['REDDIT_USERNAME'],
            'reddit_pass': os.environ['REDDIT_PASSWORD'],
            'db_name': os.environ['DB_NAME'],
            'table_name': os.environ['TABLE_NAME'],
            'db_user': os.environ['DB_USER'],
            'db_password': os.environ['DB_PASSWORD'],
            'reddit_user_agent': os.environ['REDDIT_USER_AGENT']}

def get_token(env_vars):
    """ """
    auth = requests.auth.HTTPBasicAuth(env_vars['client_id'], env_vars['secret_id'])

    data = {'grant_type': 'password',
            'username': env_vars['reddit_user'],
            'password': env_vars['reddit_pass']}

    headers = {'User-Agent': env_vars['reddit_user_agent']}

    res = requests.post(TOKEN_ENDPOINT, auth=auth, data=data, headers=headers, timeout=60)
    if res.status_code != 200:
        logger.error("Error fetching token")
        return None

    token = res.json()['access_token']
    headers = {**headers, **{'Authorization': f"bearer {token}"}}

    return headers
