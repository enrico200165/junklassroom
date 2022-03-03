
# https://developers.google.com/calendar/api/quickstart/python

from __future__ import print_function

import datetime
from os import stat
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import global_defs as gd
import little_utils_generic as lu_g

# If modifying these scopes, delete the  token
SCOPES_GCALENDAR = ['https://www.googleapis.com/auth/calendar.readonly']
log = gd.log



def get_gcalendar_service():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(gd.gcalendar_oauth_token_filepath):
        creds = Credentials.from_authorized_user_file(gd.gcalendar_oauth_token_filepath, SCOPES_GCALENDAR)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(gd.gcalendar_credentials_filepath, SCOPES_GCALENDAR)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(gd.gcalendar_oauth_token_filepath, 'w') as token:
            token.write(creds.to_json())
    try:
        service = build('calendar', 'v3', credentials=creds)
    except HttpError as error:
        log.error('An error occurred: %s' % error)
        service = None
    finally:
        return service


def weekly_appointments(start_date, week_day_number_l, end_date):
    """generate list of dates for a list of weekly day numbers, 
    where monday = 1, this is different from native numbering 
    where monday = 0
    Keyword arguments:
    start_date -- inclusive, dates generate from that date on
    week_day_number_l -- 1 for monday. [1, 4] = monday, thursday. monday has weekday 0
    """
    dates = []
    start_date = lu_g.to_datetime(start_date)
    last_date = lu_g.to_datetime(end_date)
    cur_date = start_date
    while cur_date <= last_date:
        for day_num in week_day_number_l:
            if lu_g.weekday_sunday0(cur_date.weekday()) == day_num:
                dates.append(cur_date)
        cur_date += datetime.timedelta(days=1)
    
    return dates




if __name__ == '__main__':

    def main():

        dates = weekly_appointments("2022-02-13", [0,2,4,5,6], "2022-06-01")
        # [ log.info(d, glu.weekday_sunday0(d.weekday()), glu.DAY_OF_NUMBER[glu.weekday_sunday0(d.weekday())]) for d in dates]

        for d in dates:
            print(d, lu_g.weekday_sunday0(d.weekday()), lu_g.DAY_OF_NUMBER[lu_g.weekday_sunday0(d.weekday())]) 

        exit(0)
        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        log.info('Getting the upcoming 10 events')
        service = get_gcalendar_service()
        if service is None:
            return
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            log.info('No upcoming events found.')
            return

        # Prints the start and name of the next 10 events
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            log.info(start + str(event['summary']))


    main()