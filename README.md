# stadtbib-reminder
Send email reminders using mailgun, before books are running out of time: reminders
are sent if less than 5 days are left, warnings if less than 2 days are left.

This script is tailored to the OPAX of Stadtbibliothek Moenchengladbach.

## Usage
- git clone ...
- pip install -r requirements.txt

set environment variables: 
- `RECIPIENTS=<comma separated list of email recipients>`
- `APIKEY=<api key for mailgun>`
- `BASEURL=<base url for mailgun api, e.g. https://api.eu.mailgun.net/v3/YOURDOMAIN.COM/`
- `SENDER=<from address>, e.g. stadtbib@YOURDOMAIN.COM`
- `USER=<id on the card, e.g. 05123456>`
- `PWD=<password, e.g. birthdate DDMMYYYY>`
- `UNAME=<name to be sent in notifications>`
 
Start with `venv/bin/python stadtbib-monitor.py [--list]` (if you created a venv)
Parameter --list will send an email with all books regardless of due dates.

## ToDo
There is no testing, no error handling, no reporting on failed logins, ... This is just "code that somehow works". I will need to rename some variables, esp. the env vars, introduce error handling, ...
