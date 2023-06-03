""" """
import os
import requests
import psycopg2

RSPP_ENDPOINT = 'https://oauth.reddit.com/r/redscarepodprivate'
LIMIT = 100
RECURSE = False

def get_env_vars():
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

def get_token(env_vars):
    """ """
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

def main():
    """ """
    env_vars = get_env_vars()
    print("Fetched env variables")
    conn = connect_to_db(env_vars)
    print("Connected to database")
    token = get_token(env_vars)
    print("Fetched token")
    disconnect_from_db(conn)
    print("Disconnected from database")

if __name__ == "__main__":
    main()
