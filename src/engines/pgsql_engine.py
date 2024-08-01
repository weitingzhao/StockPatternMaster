import psycopg2
from pandas import DataFrame
from psycopg2 import sql
from src import Config
from src.engines.base_engine import BaseEngine


class PgSqlEngine(BaseEngine):

    def __init__(self, config: Config):
        super().__init__(config)
        self.host = self.Config.DB_CONN.get("host")
        self.port = self.Config.DB_CONN.get("port")
        self.dbname = config.DB_CONN.get("dbname")
        self.user = config.DB_CONN.get("user")
        self.password = config.DB_CONN.get("password")

        self.db_conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            dbname=self.dbname,
            user=self.user,
            password=self.password,
        )

    def save_df(
            self,
            sql_query: str,
            df_source: DataFrame,
            execute_func: callable
    ):
        with self.db_conn.cursor() as cursor:
            insert_query = psycopg2.sql.SQL(sql_query)
            for _, row in df_source.iterrows():
                cursor.execute(insert_query, execute_func(_, row))
                self.db_conn.commit()
