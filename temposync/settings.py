import os
from dotenv import load_dotenv
load_dotenv()


JIRA_TEMPO_TOKEN = os.getenv('JIRA_TEMPO_TOKEN')
JIRA_ACCOUNT_ID = os.getenv('JIRA_ACCOUNT_ID')

LOCAL_TIMEZONE = os.getenv('LOCAL_TIMEZONE', default='UTC')
TEMPO_TIMEZONE = os.getenv('TEMPO_TIMEZONE', default='UTC')

TEMPO_BASE_URI = os.getenv('TEMPO_BASE_URI', "https://api.tempo.io/core/3")
