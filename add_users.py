import logging
import random
import sys
import time

from pathlib import Path

import praw
import prawcore

from modules.auth.auth import get_env_vars, get_token
from modules.logging.logging_setup import initialize_logging

logger = logging.getLogger(__name__)

SUBREDDIT = "LasagnaAnna"
NUM_USERS_TO_ADD = random.randrange(1, 10)

def praw_login(env_vars):
    reddit = praw.Reddit(client_id=env_vars['client_id'], client_secret=env_vars['secret_id'],
            password=env_vars['reddit_pass'], user_agent=env_vars['reddit_user_agent'],
            username=env_vars['reddit_user'])

    logger.debug(reddit)
    logger.info("Logged into Reddit")

    return reddit

def get_contributors(reddit):
    contributors = []
    for contributor in reddit.subreddit(SUBREDDIT).contributor():
        contributors.append(contributor.name)

    logger.debug(f"Fetched {len(contributors)} already added users")
    return contributors

def get_rspp_users():
    return ["walebluber", "it-speaks-for-itself", "focious-curse", "OuchieMyPwussy"]

def check_user_exists(reddit, user):
    try:
        reddit.redditor(user).id
    except prawcore.exceptions.NotFound:
        return False
    except AttributeError:
        return False

    return True

def add_users(reddit, existing, to_add):
    to_add_set = set(to_add) - set(existing)
    logger.debug(f"{len(to_add_set)} users to go!")

    users_added = 0
    for user in to_add_set:
        if users_added == NUM_USERS_TO_ADD:
            break

        user_exists = check_user_exists(reddit, user)
        if not user_exists:
            logger.info(f"User: {user} does not exist")
            continue

        logger.info(f"Adding user: {user}")
        try:
            reddit.subreddit(SUBREDDIT).contributor.add(user)
        except praw.exceptions.RedditAPIException as e:
            logger.error("Error adding user:")
            logger.error(e)
            sys.exit(1)

        users_added += 1

        logger.info("Added user")
        logger.debug("Sleeping for five seconds")
        time.sleep(5)

def add_users_wrapper():
    initialize_logging(logger, True, Path(__file__).stem)
    
    env_vars = get_env_vars()
    logger.debug("Fetched env variables")

    reddit = praw_login(env_vars)

    existing_contributors = get_contributors(reddit)
    rspp_users = get_rspp_users()
    add_users(reddit, existing_contributors, rspp_users)

if __name__ == "__main__":
    add_users_wrapper()
