""" """
import os
import requests
import psycopg2

RSPP_ENDPOINT = 'https://oauth.reddit.com/r/redscarepodprivate'
LIMIT = 100
RECURSE = False

def get_env_vars():
    print(os.environ['DB_PASSWORD'])
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
            database=os.environ['DB_NAME'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'])

    return conn

def disconnect_from_db(conn):
    """ """
    conn.close()

def main():
    """ """
    env_vars = get_env_vars()
    conn = connect_to_db(env_vars)
    print(conn)

if __name__ == "__main__":
    main()
