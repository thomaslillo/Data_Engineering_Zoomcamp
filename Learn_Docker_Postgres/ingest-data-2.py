import pandas as pd
from sqlalchemy import create_engine
from time import time
import argparse # allows us to parse command line arguments
import os

# the data source
# https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2021-01.csv


def main(params):

    # take input for the file
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url
    csv_name = params.csv_name
    
    # downlaod the csv - this step was already done so were just referencing
    # the location of the file locally
    # csv_name = '../yellow_tripdata_2021-01.csv'
    try:
        os.system(f"wget {url} -O {csv_name}")
        print(f"Downloaded file {csv_name} successfully...")
    except:
        print(f"Was unable to download file: {csv_name} ...")
    
    # create a connection to the server in docker
    # this info was defined when the psql container was built
    try:
        engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
        engine.connect()
        print("successful db connection...")
    except:
        print("error connecting to psql database...")
    
    try:
        # read in the data - uses an iterator to chunk the data into chunks of 100,000
        # this creates an iterator not a dataframe - need to use the next command
        # to get the next segment (each iteration)
        df_iter = pd.read_csv(csv_name, iterator=True, chunksize=75000)

        # get the first 5, this will be used to write headers
        df_h = pd.read_csv(csv_name, nrows=5)
        print("read data was successful...")
    except:
        print("read data operation was not successful...")

    # change the data type of some rows
    df_h.tpep_pickup_datetime = pd.to_datetime(df_h.tpep_pickup_datetime)
    df_h.tpep_dropoff_datetime = pd.to_datetime(df_h.tpep_dropoff_datetime)

    # infer the schema from the dataframe - used to create the psql table
    print(pd.io.sql.get_schema(df_h, name=table_name, con=engine))
    # this is not the greatest way to do it, but it will work for now
    
    try:
        # write the dataframe to the sql database
        df_h.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')
        print("successfully wrote the headers to a table...")
        headers_written = True
    except:
        print("writing the headers failed...")
    
    # write the dataframe to the sql database
    # this loop seems like a bad way to do it, but just following the class
    while headers_written == True:
        chunk = next(df_iter)
        try:
            t_start = time()
            # change the data type of some rows
            chunk.tpep_pickup_datetime = pd.to_datetime(chunk.tpep_pickup_datetime)
            chunk.tpep_dropoff_datetime = pd.to_datetime(chunk.tpep_dropoff_datetime)
            # write the rows to the database
            chunk.to_sql(name=table_name, con=engine, if_exists='append')
            t_end = time()
            print("inserted chunk... took %.3f seconds" % (t_end - t_start))        
        except:
            print("there was an error in the chuck writing process!")


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Ingest CSV data to Postgres")
    
    # the arguments that will be parsed
    parser.add_argument('--user', help='username for Postgres')
    parser.add_argument('--password', help='password for Postgres')
    parser.add_argument('--host', help='host for Postgres')
    parser.add_argument('--port', type=int, help='port for Postgres')
    parser.add_argument('--db', help='db name for Postgres')
    parser.add_argument('--table_name', help='table name for Postgres where we will write the results')
    # could also pass the location of the csv file in here but not this time    
    parser.add_argument('--url', help='url of the csv file')
    parser.add_argument('--csv_name', help='url of the csv file')

    args = parser.parse_args()
    
    main(args)