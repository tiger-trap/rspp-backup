""" """
import logging
import os
import sys

from pathlib import Path
import requests
import psycopg2
import psycopg2.extras

from modules.logging.logging import initialize_logging

RSPP_ENDPOINT = 'https://oauth.reddit.com/r/redscarepodprivate'
TOKEN_ENDPOINT = 'https://www.reddit.com/api/v1/access_token'
ENDPOINT_TYPE = "new"
LIMIT = 1
RECURSE = False
DEBUG = False

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
        logger.error("Error fetching token")
        sys.exit(1)

    token = res.json()['access_token']
    headers = {**headers, **{'Authorization': f"bearer {token}"}}

    return headers

def get_insert_sql_statement(env_vars):
    """ """
    sql_statement = f"INSERT INTO {env_vars['table_name']} (author, is_banned) \
            VALUES %s ON CONFLICT DO NOTHING"

    return sql_statement

def get_count_users_sql_statement(env_vars):
    """ """
    sql_statement = f"SELECT COUNT(*) FROM {env_vars['table_name']}"

    return sql_statement

def get_posts(headers, posts, after):
    """ """
    params = {'limit': LIMIT, 'after': after}
    res = requests.get(f"{RSPP_ENDPOINT}/{ENDPOINT_TYPE}",
            headers=headers, params=params, timeout=60)

    if res.status_code != 200:
        logger.error("Error fetching posts from posts endpoint")
        sys.exit(1)

    try:
        fetched_posts = res.json()['data']['children']
        for post in fetched_posts:
            posts.append(post)
    except IndexError:
        logger.error("Error parsing response from posts endpoint")
        sys.exit(1)

    logger.info("Fetched %s posts from the request", len(fetched_posts))

    if len(fetched_posts) == LIMIT and RECURSE:
        try:
            last_post = fetched_posts[-1]['data']['name']
        except IndexError:
            logger.error("Error fetching id from post")
            sys.exit(1)

        logger.info("Making recursive call")
        get_posts(headers, posts, last_post)
    else:
        logger.info("Fetched %s total posts", len(posts))

def insert_commentators(sql_statement, conn, posters):
    """ """
    cursor = conn.cursor()
    psycopg2.extras.execute_values(cursor, sql_statement, posters)
    conn.commit()
    return False

def get_commentators(headers, posts, commentators):
    """ """
    for post in posts:
        new_commentators = set()
        post_id = post['data']['id']
        logger.info("Scraping post %s", post_id)
        post_author = post['data']['author']

        new_commentators.add((post_author,False))
        logger.info("Found author %s", post_author)
        res = requests.get(f"{RSPP_ENDPOINT}/comments/{post_id}", headers=headers, timeout=60)
        if res.status_code != 200:
            logger.error("Error fetching posts with id %s. Ignoring...", post_id)
            continue

        try:
            comments = res.json()[1]['data']['children']
        except IndexError:
            logger.error("Error parsing comments from response for %s", post_id)
            continue

        for comment in comments:
            comment_author = comment['data']['author']
            new_commentators.add((comment_author,False))
            logger.info("Found author %s", comment_author)

        commentators.update(new_commentators)

def main():
    """ """
    initialize_logging(logger, DEBUG, Path(__file__).stem)

    env_vars = get_env_vars()
    logger.info("Fetched env variables")

    conn = connect_to_db(env_vars)
    logger.info("Connected to database")

    sql_statement = get_insert_sql_statement(env_vars)

    token = get_token(env_vars)
    logger.info("Fetched token")

    posts = []
    get_posts(token, posts, None)

    commentators = set()
    get_commentators(token, posts, commentators)
    logger.info("Found %s unique posters", len(commentators))

    logger.info("Writing to database")
    success = insert_commentators(sql_statement, conn, commentators)

    disconnect_from_db(conn)
    logger.info("Disconnected from database")

if __name__ == "__main__":
    main()
