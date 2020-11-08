from datetime import datetime
from urllib.parse import urlencode

import requests
from pytz import timezone

from temposync.settings import TEMPO_BASE_URI, TEMPO_TIMEZONE

tempo_tz = timezone(TEMPO_TIMEZONE)


def to_camel_case(string: str):
    """
    Don't handle irrelevant cases of '_' on either end
    """
    c0, *rest = string.split('_')
    return ''.join([c0, *[c.capitalize() for c in rest]])


class TempoError(Exception):
    pass


class TempoWorklog:
    __slots__ = [
        'jira_worklog_id',
        'tempo_worklog_id',
        'issue',
        'time_spent_seconds',
        'start_date',
        'start_time',
        'description',
        'created_at',
        'updated_at',
        'author',
    ]

    def __init__(self, values: dict):
        for slot in self.__slots__:
            key = to_camel_case(slot)
            setattr(self, slot, values[key])


class TempoAPI:
    def __init__(self, token):
        if not token or not isinstance(token, str):
            raise ValueError("Token must be a non-empty string")
        self.token = token

    def _appi(self, endpoint, method: str = 'get', params: dict = None):
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }
        query = ''
        data = None
        if params:
            if method == 'get':
                query = f'?{urlencode(params)}'
            else:
                data = params

        try:
            response = requests.request(method, f'{TEMPO_BASE_URI}/{endpoint}{query}', json=data, headers=headers)
        except requests.HTTPError as e:
            raise TempoError("Request failed") from e

        if response.status_code in (200, 201):
            return response.json()

        if method == 'delete' and response.status_code == 204:
            return True

        try:
            errors = response.json()['errors']
            if len(errors) == 1:
                message = errors[0]['message']
            else:
                message = str(errors)
        except (ValueError, KeyError, TypeError):
            message = response.text
        raise TempoError(f"{response.status_code}: {message}")

    def get_worklogs(self, issue=None):
        """
        Sample response:

        {
          "self": "https://api.tempo.io/core/3/worklogs?offset=0&limit=10",
          "metadata": {
            "count": 10,
            "offset": 0,
            "limit": 10,
            "next": "https://api.tempo.io/core/3/worklogs?offset=10&limit=10"
          },
          "results": [
            {
              "self": "https://api.tempo.io/core/3/worklogs/123",
              "tempoWorklogId": 123,
              "jiraWorklogId": 12345,
              "issue": {
                "self": "https://thorgatedigital.atlassian.net/rest/api/2/issue/PROJ-123",
                "key": "PROJ-123",
                "id": 1234
              },
              "timeSpentSeconds": 3960,
              "billableSeconds": 3960,
              "startDate": "2018-07-24",
              "startTime": "10:37:51",
              "description": "Logged for User by Automated LogWork Connect",
              "createdAt": "2018-09-16T18:07:53Z",
              "updatedAt": "2018-07-24T08:44:26Z",
              "author": {
                "self": "https://thorgatedigital.atlassian.net/rest/api/2/user?accountId=abcdef0123456789",
                "accountId": "abcdef0123456789",
                "displayName": "User Name"
              },
              "attributes": {
                "self": "https://api.tempo.io/core/3/worklogs/218/work-attribute-values",
                "values": []
              }
            },
            {"...": "..."}
          ]
        }

        :return:
        """

        params = {}
        if issue:
            params['issue'] = issue

        return self._appi('worklogs', params=params)

    def add_worklog(self, *, account_id, issue, started_at: datetime, finished_at=None, description=None):
        """
        Sample request:

        {
          "issueKey": "DUM-1",
          "timeSpentSeconds": 3600,
          "billableSeconds": 5200,
          "startDate": "2017-02-06",
          "startTime": "20:06:00",
          "description": "Investigating a problem with our external database system",
          "authorAccountId": "1111aaaa2222bbbb3333cccc",
          "attributes": [
            {
              "key": "_EXTERNALREF_",
              "value": "EXT-32548"
            }
          ]
        }

        """
        assert account_id, "Account ID is empty"

        params = {}

        if finished_at is None:
            finished_at = datetime.now()

        # Tempo plugin has no idea about timezone!
        started_at = started_at.astimezone(tempo_tz)
        finished_at = finished_at.astimezone(tempo_tz)

        params['issueKey'] = issue
        params['startDate'] = started_at.strftime('%Y-%m-%d')
        params['startTime'] = started_at.strftime('%H:%M:%S')
        params['authorAccountId'] = account_id
        params['timeSpentSeconds'] = (finished_at - started_at).seconds
        params['description'] = description or "Created by temposync"

        response = self._appi('worklogs', 'post', params=params)
        return TempoWorklog(response)

    def delete_worklog(self, worklog_id):
        return self._appi(f'worklogs/{worklog_id}', 'delete')

    def update_worklog(self, worklog_id, *, account_id, issue, started_at: datetime, finished_at: datetime,
                       description=None):
        """

        :param worklog_id:
        :param account_id:
        :param issue:
        :param started_at:
        :param finished_at:
        :param description:
        :return:
        """
        assert account_id, "Account ID is empty"

        params = {}

        # Tempo plugin has no idea about timezone!
        started_at = started_at.astimezone(tempo_tz)
        finished_at = finished_at.astimezone(tempo_tz)

        params['issueKey'] = issue
        params['startDate'] = started_at.strftime('%Y-%m-%d')
        params['startTime'] = started_at.strftime('%H:%M:%S')
        params['authorAccountId'] = account_id
        params['timeSpentSeconds'] = (finished_at - started_at).seconds
        params['description'] = description or "Created by temposync"

        response = self._appi(f'worklogs/{worklog_id}', 'put', params=params)
        return TempoWorklog(response)
