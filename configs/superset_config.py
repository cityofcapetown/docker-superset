import os
from flask_caching.backends.rediscache import RedisCache


def env(key, default=None):
    return os.getenv(key, default)


# Redis Base URL
REDIS_BASE_URL = f"{env('REDIS_PROTO')}://{env('REDIS_HOST')}:{env('REDIS_PORT')}"

# Redis URL Params
REDIS_URL_PARAMS = ""

# Build Redis URLs
CACHE_REDIS_URL = f"{REDIS_BASE_URL}/{env('REDIS_DB', 1)}{REDIS_URL_PARAMS}"
CELERY_REDIS_URL = f"{REDIS_BASE_URL}/{env('REDIS_CELERY_DB', 0)}{REDIS_URL_PARAMS}"

MAPBOX_API_KEY = env('MAPBOX_API_KEY', '')
CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'superset_',
    'CACHE_REDIS_URL': CACHE_REDIS_URL,
}
DATA_CACHE_CONFIG = CACHE_CONFIG

SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{env('DB_USER')}:{env('DB_PASS')}@{env('DB_HOST')}:{env('DB_PORT')}/{env('DB_NAME')}"
SQLALCHEMY_TRACK_MODIFICATIONS = True


class CeleryConfig:
    imports = ("superset.sql_lab",)
    broker_url = CELERY_REDIS_URL
    result_backend = CELERY_REDIS_URL


CELERY_CONFIG = CeleryConfig
RESULTS_BACKEND = RedisCache(
    host=env('REDIS_HOST'),
    port=env('REDIS_PORT'),
    key_prefix='superset_results',
)

# Overrides
# alerts_and_reports
from celery.schedules import crontab

REDIS_HOST = 'superset-redis-headless'
REDIS_PORT = '6379'


class CeleryConfig:
    BROKER_URL = 'redis://%s:%s/0' % (REDIS_HOST, REDIS_PORT)
    CELERY_IMPORTS = ('superset.sql_lab', "superset.tasks", "superset.tasks.thumbnails",)
    CELERY_RESULT_BACKEND = 'redis://%s:%s/0' % (REDIS_HOST, REDIS_PORT)
    CELERYD_PREFETCH_MULTIPLIER = 10
    CELERY_ACKS_LATE = True
    CELERY_ANNOTATIONS = {
        'sql_lab.get_sql_results': {
            'rate_limit': '100/s',
        },
        'email_reports.send': {
            'rate_limit': '1/s',
            'time_limit': 600,
            'soft_time_limit': 600,
            'ignore_result': True,
        },
    }
    CELERYBEAT_SCHEDULE = {
        'reports.scheduler': {
            'task': 'reports.scheduler',
            'schedule': crontab(minute='*', hour='*'),
        },
        'reports.prune_log': {
            'task': 'reports.prune_log',
            'schedule': crontab(minute=0, hour=0),
        },
    }


CELERY_CONFIG = CeleryConfig

SCREENSHOT_LOCATE_WAIT = 10
SCREENSHOT_LOAD_WAIT = 60

# custom_sso_security_manager
from pprint import pprint
import logging
from superset.security import SupersetSecurityManager
from flask_appbuilder.security.manager import AUTH_OAUTH

log = logging.getLogger(__name__)


class GitlabSecurityManager(SupersetSecurityManager):
    def oauth_user_info(self, provider, response=None):
        if provider == 'gitlab':
            log.info('Handling Gitlab OAuth response')
            me = self.appbuilder.sm.oauth_remotes[provider].get('user').json()
            pprint("Print statement")
            pprint(me)
            log.info("user_data: {0}".format(me))
            name = me.get('name', '')
            first_name = ''
            last_name = ''
            if ' ' in name:
                s = name.split(' ')
                first_name = s[0]
                last_name = s[1]
            data = {'username': me.get('username', ''),
                    'email': me.get('email', ''),
                    'first_name': first_name,
                    'last_name': last_name}
            log.info('Gitlab Response: {}'.format(data))
            return data
        return {}


# Monkey patch the SSL library to avoid certificate verification
# ssl._create_default_https_context = ssl._create_unverified_context

# enable_oauth
ENABLE_PROXY_FIX = True
PROXY_FIX_CONFIG = {"x_for": 1, "x_proto": 1, "x_host": 1, "x_port": 1, "x_prefix": 1}
# SQL_ALCHEMY_DATABASE_URI = 'sqlite:////var/lib/superset/superset.db'
CUSTOM_SECURITY_MANAGER = GitlabSecurityManager
AUTH_TYPE = AUTH_OAUTH
OAUTH_PROVIDERS = [{
    'name': 'gitlab',
    'icon': 'fa-gitlab',
    'token_key': 'access_token',
    'remote_app': {
        'client_id': env('GITLAB_OAUTH_CLIENT_ID'),
        'client_secret': env('GITLAB_OAUTH_CLIENT_SECRET'),
        'server_metadata_url': 'https://ds1.capetown.gov.za/ds_gitlab/.well-known/openid-configuration',
        'client_kwargs': {
            'scope': 'openid read_user'
        },
        'access_token_method': 'POST',
        'api_base_url': 'https://ds1.capetown.gov.za/ds_gitlab/api/v4/',
        'request_token_params': {
            'scope': 'openid read_user'
        },
        'access_token_url': 'https://ds1.capetown.gov.za/ds_gitlab/oauth/token',
        'authorize_url': 'https://ds1.capetown.gov.za/ds_gitlab/oauth/authorize',

    }
}]
AUTH_ROLE_ADMIN = 'Admin'
AUTH_ROLE_PUBLIC = 'Public'
AUTH_ROLE_GAMMA = 'Gamma'
AUTH_USER_REGISTRATION = True
AUTH_USER_REGISTRATION_ROLE = "Gamma"
PUBLIC_ROLE_LIKE = "Gamma"

# enable_thumbnails
from superset.superset_typing import CacheConfig

THUMBNAIL_SELENIUM_USER = "admin"

from superset.utils.urls import headless_url
from superset.utils.machine_auth import MachineAuthProvider


def auth_driver(driver, user):
    # Setting cookies requires doing a request first, but /login is redirected to oauth provider, and stuck there.
    driver.get(headless_url("/doesnotexist"))

    cookies = MachineAuthProvider.get_auth_cookies(user)

    for cookie_name, cookie_val in cookies.items():
        driver.add_cookie(dict(name=cookie_name, value=cookie_val))

    return driver


WEBDRIVER_AUTH_FUNC = auth_driver

REDIS_HOST = 'superset-redis-headless'
REDIS_PORT = '6379'

THUMBNAIL_CACHE_CONFIG: CacheConfig = {
    'CACHE_TYPE': 'redis',
    'CACHE_DEFAULT_TIMEOUT': 60 * 60 * 24 * 7,
    'CACHE_KEY_PREFIX': 'superset_thumbnail',
    'CACHE_REDIS_URL': 'redis://%s:%s/0' % (REDIS_HOST, REDIS_PORT),
    "CACHE_NO_NULL_WARNING": True,
}
# WEBDRIVER_TYPE= "chrome"
WEBDRIVER_BASEURL = "https://superset-dev.capetown.gov.za"
WEBDRIVER_BASEURL_USER_FRIENDLY = "https://superset-dev.capetown.gov.za"

# feature_flags
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
    "ALERT_REPORTS": True,
    "THUMBNAILS": True,
    "LISTVIEWS_DEFAULT_CARD_VIEW": True,
    "DASHBOARD_NATIVE_FILTERS": True,
    "DASHBOARD_CROSS_FILTERS": True,
    "ENABLE_JAVASCRIPT_CONTROLS": True}

# row_limit
# this increases the row limit to 2M
ROW_LIMIT = 2000000
SQL_MAX_ROW = 2000000
# DEFAULT_SQLLAB_LIMIT = 2000000
QUERY_SEARCH_LIMIT = 2000000
FILTER_ROW_LIMIT = 2000000

# secret
# FAB secret. Need to generate yourself
# SECRET_KEY = "\2\1thisismyscretkey\1\2\e\y\y\h"

# smtp
import ast

SMTP_HOST = env("SMTP_HOST", "mail.capetown.gov.za")
SMTP_STARTTLS = ast.literal_eval(env("SMTP_STARTTLS", "False"))
SMTP_SSL = ast.literal_eval(env("SMTP_SSL", "False"))
SMTP_USER = env("SMTP_USER", "superset")
SMTP_PORT = env("SMTP_PORT", 25)
SMTP_PASSWORD = env("SMTP_PASSWORD", "")
SMTP_MAIL_FROM = env("SMTP_MAIL_FROM", "")

# tooltips
# NB: this will move to a feature flag in v2
ENABLE_JAVASCRIPT_CONTROLS = True