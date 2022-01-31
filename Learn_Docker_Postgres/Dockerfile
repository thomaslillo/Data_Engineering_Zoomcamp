# this file tells docker what to do in order

# list of things to run to create a new image
FROM python:3.9

# a command to run in the container when it starts
RUN  pip install pandas sqlalchemy psycopg2
RUN apt-get install wget

# the working directory we will use in the container
WORKDIR /app

# copy file from source to destination in the container we launch
COPY ingest-data-2.py ingest-data-2.py

# the entry point of the program
ENTRYPOINT [ "python", "ingest-data-2.py" ]
# ENTRYPOINT [ "bash" ]
# could do ENTRYPOINT ["python", "pipeline.py"]