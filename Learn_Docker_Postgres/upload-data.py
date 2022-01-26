import pandas as pd
from sqlalchemy import create_engine
from time import time

# the data source
# https://s3.amazonaws.com/nyc-tlc/trip+data/yellow_tripdata_2021-01.csv

def main():
    
    # create a connection to the server in docker
    # this info was defined when the psql container was built
    try:
        engine = create_engine('postgresql://root:root@localhost:5432/ny_taxi')
        engine.connect()
    except:
        print("error connecting to psql database")
    
    # read in the data - uses an iterator to chunk the data into chunks of 100,000
    # this creates an iterator not a dataframe - need to use the next command
    # to get the next segment (each iteration)
    df_iter = pd.read_csv('../yellow_tripdata_2021-01.csv', iterator=True, chunksize=100000)

    # get the first 100,000
    df_h = pd.read_csv('../yellow_tripdata_2021-01.csv', nrows=5)

    # what is it
    print(type(df_iter))

    # change the data type of some rows
    df_h.tpep_pickup_datetime = pd.to_datetime(df_h.tpep_pickup_datetime)
    df_h.tpep_dropoff_datetime = pd.to_datetime(df_h.tpep_dropoff_datetime)

    # infer the schema from the dataframe - used to create the psql table
    print(pd.io.sql.get_schema(df_h, name='yellow_taxi_data', con=engine))
    # this is not the greatest way to do it, but it will work for now
    
    try:
        # write the dataframe to the sql database
        df_h.head(n=0).to_sql(name='yellow_taxi_data', con=engine, if_exists='replace')
    except:
        print("writing the headers failed")
    
    # write the dataframe to the sql database
    while True:
        chunk = next(df_iter)
        try:
            t_start = time()
            # change the data type of some rows
            chunk.tpep_pickup_datetime = pd.to_datetime(chunk.tpep_pickup_datetime)
            chunk.tpep_dropoff_datetime = pd.to_datetime(chunk.tpep_dropoff_datetime)
            # write the rows to the database
            chunk.to_sql(name='yellow_taxi_data', con=engine, if_exists='append')
            t_end = time()
            print("inserted chunk... took %.3f seconds" % (t_end - t_start))        
        except:
            print("there was an error in the chuck writing process")
            
if __name__ == "__main__":
    main()