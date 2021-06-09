FROM apache/superset:latest

# Switching to root to install the required packages
USER root

# For oauth
RUN pip install authlib

# For web reports
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt install -y ./google-chrome-stable_current_amd64.deb && \
    wget https://chromedriver.storage.googleapis.com/88.0.4324.96/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    chmod +x chromedriver && \
    mv chromedriver /usr/bin && \
    rm -f google-chrome-stable_current_amd64.deb chromedriver_linux64.zip && \
    pip install gevent

# Install base drivers required for helm chart to work
RUN pip install psycopg2==2.8.5 \
 && pip install redis==3.2.1 \
# Install database connectors
# Find which driver you need based on the analytics database
# you want to connect to here:
# https://superset.apache.org/installation.html#database-dependencies
# Presto
&& pip install pyhive \
# Trino - presto clone
 && pip install sqlalchemy-trino \
# MS SQL Server
 && pip install pymssql \
# HANA
 && pip install sqlalchemy-hana \
# Elastisearch
 && pip install elasticsearch-dbapi

# Switching back to using the `superset` user
USER superset
