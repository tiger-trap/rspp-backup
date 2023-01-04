import os, requests, psycopg2

RSPP_ENDPOINT = 'https://oauth.reddit.com/r/redscarepodprivate'
LIMIT = 25

def get_env_vars():
    return {'client_id': os.environ['CLIENT_ID'],
            'secret_id': os.environ['SECRET_ID'],
            'reddit_user': os.environ['REDDIT_USERNAME'],
            'reddit_pass': os.environ['REDDIT_PASSWORD'],
            'db_name': os.environ['DB_NAME'],
            'table_name': os.environ['TABLE_NAME'],
            'db_user': os.environ['DB_USER'],
            'db_password': os.environ['DB_PASSWORD']}

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

def connect_to_db(env_vars):
    conn = psycopg2.connect(
            host="localhost",
            database=env_vars['db_name'],
            user=env_vars['db_user'],
            password=env_vars['db_password'])

    return conn

def disconnect_from_db(conn):
    conn.close()

def get_commentators(headers, env_vars, conn, after, recurse):
    sql_statement = f"INSERT INTO {env_vars['table_name']} VALUES (%s, %s, %s) \
                ON CONFLICT DO NOTHING"

    params = {'limit': LIMIT, 'after': after}
    res = requests.get(f"{RSPP_ENDPOINT}/new", headers=headers, params=params)

    posts = res.json()['data']['children']

    cursor = conn.cursor()

    for post in posts:
        post_id = post['data']['id']
        post_name = post['data']['name']
        print(post_id)
        author = post['data']['author']
        cursor.execute(sql_statement, (author, False, False))
        conn.commit()
        print(f'Author: {author}')

        res = requests.get(f'{RSPP_ENDPOINT}/comments/{post_id}', headers=headers)
        comments = res.json()[1]['data']['children']

        commentators = []
        for comment in comments:
            c_author = comment['data']['author']
            #print(f"Writing: {c_author}")
            commentators.append((c_author,False,False,))

        cursor.executemany(sql_statement, commentators)
        conn.commit()

        after = post_name

        print("-----------------------------------------------------------------")

    cursor.close()

    if len(posts) == LIMIT and recurse == True:
        print("\t\tRECURSIVE CALL")
        get_commentators(headers, env_vars, conn, after)
    else:
        print(len(posts))

if __name__ == "__main__":
    env_vars = get_env_vars()
    headers = get_token(env_vars)
    conn = connect_to_db(env_vars)
    get_commentators(headers, env_vars, conn, "", False)
    disconnect_from_db(conn)
