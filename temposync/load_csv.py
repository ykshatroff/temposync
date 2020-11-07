import os
from collections import namedtuple
import csv
import re
import datetime as dt
import click
from pytz import timezone

from temposync import settings
from temposync.tempo_api import TempoAPI, TempoError

TogglTimerEntry = namedtuple(
    'TogglTimerEntry',
    'User,Email,Client,Project,Task,Description,Billable,StartDate,StartTime,EndDate,EndTime,Duration,Tags,Amount'
)

WorkLog = namedtuple('WorkLog', 'task_id,description,started_at,finished_at')


def project_to_env_var(prj):
    res = re.sub(r'\W', '_', prj)
    res = res.upper()
    return 'TOGGL_%s_ISSUE' % res


@click.command()
@click.argument('filename')
@click.option('--sync', '-s', is_flag=True, default=False, help='Perform sync to Tempo.')
@click.option('--ignore-untagged', '-i', is_flag=True, default=False,
              help='Ignore entries that have neither an issue key nor project.')
@click.option('--remove-file', '-r', is_flag=True, help='Remove the processed CSV file.')
def load_csv(filename, sync, ignore_untagged, remove_file):
    print(f"Loading data from CSV file {filename}, sync={sync}")

    my_tz = timezone(settings.LOCAL_TIMEZONE)

    # I know some TZs use fractions of an hour, this is expedient for now
    tzoffset = my_tz.utcoffset(dt.datetime.now()).seconds // 3600
    tzoffset = f"+{tzoffset:02d}:00"
    print(f"Your timezone offset is {tzoffset}")

    entries = []

    with open(filename, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        skip_row = next(csv_reader)
        assert skip_row[1] == f'Email', f'The first row should be headers, but is {skip_row}'

        print("")
        print("*** Entries ***")
        print("")

        for line_number, row in enumerate(csv_reader, start=2):
            entry = TogglTimerEntry(*row)
            description = entry.Description
            jira_issue = re.match('([a-z]+-[0-9]+)[:. ]?(.*)', description, re.IGNORECASE)
            if not jira_issue:
                prj_env_var = project_to_env_var(entry.Project)
                key = os.getenv(prj_env_var)
                if not key:
                    if ignore_untagged:
                        print(f"Skipping entry {line_number}:\n  ", entry.Description)
                        continue
                    raise ValueError(f"Untagged entry at line {line_number}: {entry.Description}")
            else:
                key = jira_issue.group(1)
                description = jira_issue.group(2).strip()

            start_date = dt.datetime.fromisoformat(f'{entry.StartDate} {entry.StartTime}{tzoffset}')
            end_date = dt.datetime.fromisoformat(f'{entry.EndDate} {entry.EndTime}{tzoffset}')

            print(f"{key}: {description}, started at {start_date.isoformat()}")
            description = f"{description} (Import from Toggl)".strip()
            entries.append(
                WorkLog(task_id=key, description=description, started_at=start_date, finished_at=end_date))

    if not sync:
        print("*** To sync entries, add the -s flag ***")
        return

    print("")
    print("*** Syncing entries ***")
    print("")

    api = TempoAPI(settings.JIRA_TEMPO_TOKEN)

    for worklog in entries:
        try:
            tempo_worklog = api.add_worklog(
                account_id=settings.JIRA_ACCOUNT_ID,
                issue=worklog.task_id,
                started_at=worklog.started_at,
                finished_at=worklog.finished_at,
                description=worklog.description
            )
        except TempoError as e:
            print(f"Failed to add {worklog.task_id} ({worklog.started_at}) Error: ", e)
            continue
        print(f"Added {worklog.task_id} ({worklog.started_at})", tempo_worklog.jira_worklog_id)

    if remove_file:
        os.remove(filename)


if __name__ == '__main__':
    load_csv()
