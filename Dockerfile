FROM apache/superset:latest

# Switching to root to install the required packages
USER root

# For oauth
RUN pip install authlib

# For web reports
RUN pi install gevent

# Install base drivers required for helm chart to work
RUN pip install psycopg2==2.8.5
RUN pip install redis==3.2.1

# Find which driver you need based on the analytics database
# you want to connect to here:
# https://superset.apache.org/installation.html#database-dependencies

# Presto
RUN pip install pyhive
# Trino - presto clone
RUN pip install sqlalchemy-trino

# MS SQL Server
RUN pip install pymssql

# HANA
RUN pip install sqlalchemy-hana

# Switching back to using the `superset` user
USER superset
