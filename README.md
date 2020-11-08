# temposync
Sync work logs with Jira Tempo.

Currently works with Toggl reports in CSV format.

## Prerequisites:

* `python` **>= 3.6**

## Usage

* Create virtualenv and install the package
```
python -m venv --prompt=temposync .venv
source .venv/bin/activate 
pip install -e .
```
* Create a `.env` file in the project directory 
  with your Jira account id and Tempo API token. The `.env.example` file
  can serve as a template, just copy it to `.env` and fill out the keys.
* Download a report from Toggl in CSV format
* Run `temposync <FILENAME.csv>`, it shows the log entries found in the file.
* To perform a real sync with Tempo, add the `-s` key.

## Rules

The Toggl log entry text must begin with a Jira issue key, followed by a space, dot, or colon:
```
PROJ-555: doing cool stuff
```
The rest of the text will be set as the Tempo log entry description.

If there is no issue key in the beginning, the entry may be assigned to a project in Toggl 
and the corresponding project added to `.env` as follows:
```
TOGGL_MYPROJECT_ISSUE=MYPROJ-555
```  
-- that is, assuming the project name of 'MyProject', entries assigned to `MyProject` in Toggl
will be mapped to the issue key `MYPROJ-555`.

The project name from toggl will be mapped to a `.env` entry as follows:
* all non-ascii-alphanumeric characters will be replaced with `_`;
* the result string will be uppercased;
* the result string will be inserted into the template `TOGGL_%s_ISSUE`.

The `temposync` command fails if an entry is tagged with neither an issue key nor a project.
To change this behavior, use the `-i` key (`--ignore-untagged`), and such issues will be skipped.

## Gotchas

The Tempo API has no concept of timezone, all times are sent in a timezone-agnostic fashion.
In case your current local timezone is different from Tempo's (e.g. you're traveling),
specify the timezones you and Tempo are in in the `.env` file. If it is omitted,
it can lead to times in tempo being off by some hours.

The personal Tempo timezone is configured in _Account settings_. 
