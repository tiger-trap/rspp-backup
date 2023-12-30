""" """
import argparse
import logging
import sys

from pathlib import Path
import requests

from modules.auth.auth import get_env_vars, get_token
from modules.database.database import (connect_to_db, disconnect_from_db,
        get_insert_sql_statement, get_count_users_sql_statement, insert_commentators, count_users)
from modules.logging.logging_setup import initialize_logging

RSPP_ENDPOINT = 'https://oauth.reddit.com/r/redscarepodprivate'
LIMIT = 100

logger = logging.getLogger(__name__)


def get_approved_submitters(headers, submitters, after, recurse):
    params = {'limit': LIMIT, 'after': after}
    res = requests.get(f"{RSPP_ENDPOINT}/about/contributors",
            headers=headers, params=params, timeout=60)
    if res.status_code != 200:
        logger.error(f"Error fetching contributors with status code: {res.status_code}")
        logger.error(f"{res.json()}")
        return

    try:
        contributors = res.json()['data']['children']
    except IndexError:
        logger.error("Error parsing contributors")
        logger.error(f"{res.json()}")
        return

    for contributor in contributors:
        name = contributor['name']
        user_id = contributor['id']
        print(f"Fetching user: {name} ({user_id})")
        submitters.add((name,user_id))

    if len(contributors) == LIMIT and recurse:
        try:
            last_user = contributors[-1]['rel_id']
        except IndexError:
            logger.error("Error fetching id from user data")
            return

        logger.info("Making recursive call")
        get_approved_submitters(headers, submitters, last_user, recurse)
    else:
        logger.info(f"Fetched {len(submitters)} total users")

def fetch_users_wrapper(recurse, debug_logs):
    """ """

    initialize_logging(logger, debug_logs, Path(__file__).stem)

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

    submitters = set()
    get_approved_submitters(token, submitters, None, recurse)

    logger.info("Writing to database")
    insert_commentators(insert_sql_statement, conn, submitters)

    num_users = count_users(count_sql_statement, conn)
    logger.info("Current number of users in database: %s", num_users)

    disconnect_from_db(conn)
    logger.info("Disconnected from database")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            prog="RSPP backup script",
            description="Gets all approved submitters to rspp")

    parser.add_argument("-r", "--recurse", action="store_true")
    parser.add_argument("-d", "--debug", action="store_true")
    args = parser.parse_args()
    
    recurse = args.recurse
    debug_logs = args.debug

    fetch_users_wrapper(recurse, debug_logs)
