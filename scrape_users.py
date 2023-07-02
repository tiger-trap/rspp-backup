""" """
import logging
import sys

from pathlib import Path
import requests

from modules.auth.auth import get_env_vars, get_token
from modules.database.database import (connect_to_db, disconnect_from_db,
        get_insert_sql_statement, get_count_users_sql_statement, insert_commentators, count_users)
from modules.logging.logging_setup import initialize_logging

RSPP_ENDPOINT = 'https://oauth.reddit.com/r/redscarepodprivate'
ENDPOINT_TYPE = "new"
LIMIT = 100
RECURSE = True
DEBUG = False

logger = logging.getLogger(__name__)

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

    insert_sql_statement = get_insert_sql_statement(env_vars)
    count_sql_statement = get_count_users_sql_statement(env_vars)

    num_users = count_users(count_sql_statement, conn)
    logger.info("Current number of users in database: %s", num_users)

    token = get_token(env_vars)
    if token is None:
        sys.exit(1)
    logger.info("Fetched token")

    posts = []
    get_posts(token, posts, None)

    commentators = set()
    get_commentators(token, posts, commentators)
    logger.info("Found %s unique posters", len(commentators))

    logger.info("Writing to database")
    insert_commentators(insert_sql_statement, conn, commentators)

    num_users = count_users(count_sql_statement, conn)
    logger.info("Current number of users in database: %s", num_users)

    disconnect_from_db(conn)
    logger.info("Disconnected from database")

if __name__ == "__main__":
    main()
