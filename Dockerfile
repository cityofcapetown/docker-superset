FROM apache/superset:1.5.3

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

RUN export CHROMEDRIVER_VERSION=$(curl --silent https://chromedriver.storage.googleapis.com/LATEST_RELEASE_100) && \
    wget -q https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip -d /usr/bin && \
    chmod 755 /usr/bin/chromedriver && \
    rm -f chromedriver_linux64.zip

ARG GECKODRIVER_VERSION=v0.28.0
ARG FIREFOX_VERSION=88.0

# geckodriver
RUN wget https://github.com/mozilla/geckodriver/releases/download/${GECKODRIVER_VERSION}/geckodriver-${GECKODRIVER_VERSION}-linux64.tar.gz -O /tmp/geckodriver.tar.gz && \
    tar xvfz /tmp/geckodriver.tar.gz -C /tmp && \
    mv /tmp/geckodriver /usr/local/bin/geckodriver && \
    rm /tmp/geckodriver.tar.gz

# Install Firefox
RUN wget https://download-installer.cdn.mozilla.net/pub/firefox/releases/${FIREFOX_VERSION}/linux-x86_64/en-US/firefox-${FIREFOX_VERSION}.tar.bz2 -O /opt/firefox.tar.bz2 && \
    tar xvf /opt/firefox.tar.bz2 -C /opt && \
    ln -s /opt/firefox/firefox /usr/local/bin/firefox

# Install base drivers required for helm chart to work
RUN pip install gevent \
 && pip install psycopg2==2.9.1 \
 && pip install redis==3.5.3 \
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

# Pinning various packages to fix dependency issues
RUN pip3 install --no-cache --no-deps --force-reinstall alembic==1.11.1 markupsafe==2.0.1 pyopenssl==22.1.0 importlib-metadata==4.13.0 importlib-resources==5.12.0 sqlalchemy==1.3.23

# Switching back to using the `superset` user
USER superset
