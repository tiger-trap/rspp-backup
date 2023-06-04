""" """
import logging
import os
import sys

import requests
import psycopg2

RSPP_ENDPOINT = 'https://oauth.reddit.com/r/redscarepodprivate'
TOKEN_ENDPOINT = 'https://www.reddit.com/api/v1/access_token'
LIMIT = 100
RECURSE = True

def get_env_vars():
    """ """
    return {'client_id': os.environ['CLIENT_ID'],
            'secret_id': os.environ['SECRET_ID'],
            'reddit_user': os.environ['REDDIT_USERNAME'],
            'reddit_pass': os.environ['REDDIT_PASSWORD'],
            'db_name': os.environ['DB_NAME'],
            'table_name': os.environ['TABLE_NAME'],
            'db_user': os.environ['DB_USER'],
            'db_password': os.environ['DB_PASSWORD']}

def connect_to_db(env_vars):
    """ """
    conn = psycopg2.connect(
            host="localhost",
            database=env_vars['db_name'],
            user=env_vars['db_user'],
            password=env_vars['db_password'])

    return conn

def disconnect_from_db(conn):
    """ """
    conn.close()

def get_token(env_vars):
    """ """
    auth = requests.auth.HTTPBasicAuth(env_vars['client_id'], env_vars['secret_id'])

    data = {'grant_type': 'password',
            'username': env_vars['reddit_user'],
            'password': env_vars['reddit_pass']}

    headers = {'User-Agent': 'rspp/0.1.1'}

    res = requests.post(TOKEN_ENDPOINT, auth=auth, data=data, headers=headers, timeout=60)
    if res.status_code != 200:
        logging.error("Error fetching token")
        sys.exit(1)

    token = res.json()['access_token']
    headers = {**headers, **{'Authorization': f"bearer {token}"}}

    return headers

def get_sql_statement(env_vars):
    """ """
    sql_statement = f"INSERT INTO {env_vars['table_name']} VALUES (%s, %s, %s) \
            ON CONFLICT DO NOTHING"

    return sql_statement

def get_posts(headers, posts, after):
    """ """
    params = {'limit': LIMIT, 'after': after}
    res = requests.get(f"{RSPP_ENDPOINT}/new", headers=headers, params=params, timeout=60)
    if res.status_code != 200:
        logging.error("Error fetching posts from posts endpoint")
        sys.exit(1)

    try:
        fetched_posts = res.json()['data']['children']
        for post in fetched_posts:
            posts.append(post)
    except IndexError:
        logging.error("Error parsing response from posts endpoint")
        sys.exit(1)

    logging.info("Fetched %s posts from the request", len(fetched_posts))

    if len(fetched_posts) == LIMIT and RECURSE:
        try:
            last_post = fetched_posts[-1]['data']['name']
        except IndexError:
            logging.error("Error fetching id from post")
            sys.exit(1)

        logging.info("Making recursive call")
        get_posts(headers, posts, last_post)
    else:
        logging.info("Fetched %s total posts", len(posts))

def main():
    """ """
    logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

    env_vars = get_env_vars()
    logging.info("Fetched env variables")

    conn = connect_to_db(env_vars)
    logging.info("Connected to database")

    sql_statement = get_sql_statement(env_vars)

    token = get_token(env_vars)
    logging.info("Fetched token")

    posts = []
    get_posts(token, posts, None)
    print(len(posts))

    disconnect_from_db(conn)
    logging.info("Disconnected from database")

if __name__ == "__main__":
    main()
