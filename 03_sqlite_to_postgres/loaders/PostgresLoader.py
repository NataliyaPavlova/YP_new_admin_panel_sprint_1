import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import execute_batch
from tablesClasses import FIELDS, FilmWork


class PostgresLoader:

    def __init__(self, connection: _connection):
        self.conn = connection

    def upload_data(self, table: str, data: list, batch_size):
        """Do upload to Postgres"""
        # Create a list of tuples from the list of dataclass objects
        data_to_insert = []
        for dataclass_object in data:
            row_to_insert = tuple(getattr(dataclass_object, field) for field in FIELDS[table])
            data_to_insert.append(row_to_insert)

        # form sql statement to execute
        cols = ','.join(FIELDS[table])
        cols = "{0},{1},{2}".format(cols, 'created', 'modified')
        vals = ','.join(['%s' for col in FIELDS[table]])
        vals = "{0},NOW(),NOW()".format(vals)
        query = "INSERT INTO content.{0} ({1}) VALUES ({2}) ON CONFLICT(id) DO NOTHING".format(table, cols, vals)
        cur = self.conn.cursor()

        try:
            execute_batch(cur, query, data_to_insert, page_size=batch_size)
            self.conn.commit()
            rows_number = len(data)
            print("Successfully inserted {0} rows into {1} table".format(rows_number, table))

        except (Exception, psycopg2.DatabaseError) as error:
            print("Error: {0}".format(error))
            self.conn.rollback()