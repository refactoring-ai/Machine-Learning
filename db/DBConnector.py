import mysql.connector
import pandas as pd
import hashlib
import os.path
import configparser

from pandas.core.frame import DataFrame
from configs import USE_CACHE, DB_AVAILABLE, CACHE_DIR_PATH, SHOW_SQL
from utils.log import log
import sshtunnel

config = configparser.ConfigParser()
config.read(os.path.join(os.getcwd(), 'dbconfig.ini'))

# connect to the mysql database either via ssh tunnel or directly
mydb, tunnel = None, None
if DB_AVAILABLE and config["db"].getboolean("use_tunnel"):
    tunnel = sshtunnel.SSHTunnelForwarder(
        (config["ssh_tunnel"]["host"], int(config["ssh_tunnel"]["port"])),
        ssh_username=config["ssh_tunnel"]["user"],
        ssh_password=config["ssh_tunnel"]["pwd"],
        remote_bind_address=(config["db"]["host"], int(config["db"]["port"]))
    )
    tunnel.start()
    mydb = mysql.connector.connect(
        user=config["db"]["user"],
        password=config["db"]["pwd"],
        host="127.0.0.1",
        port=tunnel.local_bind_port,
        database=config["db"]["database"],
    )
elif DB_AVAILABLE:
    mydb = mysql.connector.connect(
        host=config['db']["host"],
        user=config['db']["user"],
        passwd=config['db']["pwd"],
        database=config['db']["database"]
    )


# this method executes the query and stores the result in a local cache.
# we do not want to re-execute large queries.
# derived from
# https://medium.com/gousto-engineering-techbrunch/hash-caching-query-results-in-python-2d00f8058252
def execute_query(sql_query) -> DataFrame:
    """
    Method to query data from Redshift and return pandas dataframe
    Parameters
    ----------
    sql_query : str
        saved SQL query
    Returns
    -------
    df_raw : DataFrame
        Pandas DataFrame with raw data resulting from query
    """
    if SHOW_SQL:
        log(f"Fetch data from the db with this query: \n\n{sql_query}\n\n")

    # Hash the query
    query_hash = hashlib.sha1(sql_query.encode()).hexdigest()

    # Create the filepath
    cache_dir = os.path.join(CACHE_DIR_PATH, "cache")
    file_path = os.path.join(cache_dir, f"{query_hash}.ftr")
    df: DataFrame
    # Read the file or execute query
    if DB_AVAILABLE and not os.path.exists(file_path):
        try:
            if not os.path.isdir(cache_dir):
                os.makedirs(cache_dir)
            # split large tables into smaller chunks, to avoid MemoryErrors on
            # small machines
            df = pd.read_sql_query(
                sql_query, mydb, coerce_float=False, index_col="index")
            if USE_CACHE:
                log(f"saving cache to {file_path}")
                df.reset_index().to_feather(file_path)
        except (KeyboardInterrupt):
            if os.path.exists(file_path):
                os.remove(file_path)
            close_connection()
            exit()

    if USE_CACHE and os.path.exists(file_path):
        # log(f"using cache at {file_path}")
        df = pd.read_feather(file_path)
        df.set_index("index", inplace=True)
    else:
        raise RuntimeError(
            "Cache not found, and db connection is not available")
    return df


def close_connection():
    """
    Close the connections with the database and tunnel, if necessary.
    """
    if mydb is not None:
        mydb.close()
    if tunnel is not None:
        tunnel.close()
