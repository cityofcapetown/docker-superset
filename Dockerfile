#FROM apache/superset:b35645c3f4db8526c12ef88d9056a348fcc1f249
FROM apache/superset:1.3.1

# Switching to root to install the required packages
USER root

# For oauth
RUN pip install authlib

# For alerts and reports
RUN apt-get update && \
    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y --no-install-recommends ./google-chrome-stable_current_amd64.deb && \
    rm -f google-chrome-stable_current_amd64.deb && \
    apt-get install -y redis-server

RUN export CHROMEDRIVER_VERSION=$(curl --silent https://chromedriver.storage.googleapis.com/LATEST_RELEASE_94) && \
    wget -q https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip -d /usr/bin && \
    chmod 755 /usr/bin/chromedriver && \
    rm -f chromedriver_linux64.zip

RUN pip install --no-cache gevent psycopg2 redis

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

# Install prophet for forecasting functionality
# Install pystan with pip before using pip to install prophet
# pystan>=3.0 is currently not supported
RUN pip install pystan==2.19.1.1 \
 && pip install prophet 

# Switching back to using the `superset` user
USER superset
