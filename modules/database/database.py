""" """
import logging

import psycopg2
import psycopg2.extras

logger = logging.getLogger(__name__)

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

def get_insert_sql_statement(env_vars):
    """ """
    sql_statement = f"INSERT INTO {env_vars['table_name']} (author, userid) \
            VALUES %s ON CONFLICT DO NOTHING"

    return sql_statement

def get_count_users_sql_statement(env_vars):
    """ """
    sql_statement = f"SELECT COUNT(*) FROM {env_vars['table_name']}"

    return sql_statement

def insert_commentators(sql_statement, conn, posters):
    """ """
    cursor = conn.cursor()
    psycopg2.extras.execute_values(cursor, sql_statement, posters)
    conn.commit()

def count_users(sql_statement, conn):
    """ """
    cursor = conn.cursor()
    cursor.execute(sql_statement)

    rowcount = cursor.fetchone()[0]

    conn.commit()
    return rowcount
