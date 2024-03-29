# from projectcars import pypsycopg, pysqlalchemy
from influx2postgres import influxpg, db_name, schema_name, table_name
from settings import settings, sql_file_query
import gc


def main():
    # run projectcars using psycopg2 library
    # pypg = pypsycopg.Carpsyco(settings["postgres"])
    # run projectcars using sqlalchemy library
    # pypg = pysqlalchemy.Caralchemy(settings["postgres"])
    
    # read from influx measurement as dataframe and save it to postgres table
    pypg = influxpg.Influxpg(settings)
    pypg.create_connection(db_name=db_name)
    # pypg.get_table_info(schema_name=schema_name, table_name = table_name)
    # exectute sql queries from file
    pypg.conn.execute(sql_file_query)
    # close postgres connection
    pypg.close_connection()
    del pypg
    gc.collect()


if __name__ == "__main__":
    main()
