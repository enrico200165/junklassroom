
import os.path
import logging as log

from google.auth import credentials
from google.auth.exceptions import RefreshError

# conda install -c conda-forge google-api-python-client
from googleapiclient.discovery import build
# googleapiclient:  conda install -c conda-forge google-api-python-client
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

import global_defs as g


def try_session(credentials, scopes):

        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(g.glcassroom_oauth_token_filepath):
            creds = Credentials.from_authorized_user_file(g.glcassroom_oauth_token_filepath, scopes)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials, scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(g.glcassroom_oauth_token_filepath, 'w') as token:
                token.write(creds.to_json())

        service = build('classroom', 'v1', credentials=creds)

        return service


gclassroom_service = None

def session(credentials, scopes, terminate_on_fail = True):

    global gclassroom_service

    if gclassroom_service is not None:
        return gclassroom_service
    for i in range(3):
        try:
            service = try_session(credentials, scopes)
            gclassroom_service = service
            return service
        except RefreshError as e:
            log.warn("eccezione:",e)
            os.remove(g.glcassroom_oauth_token_filepath)
        except Exception as e:
            log.warn("eccezione",e)
    if terminate_on_fail:
        log.error("Unable to get service, terminating (is internet connection working?)")
        exit(1)

    return None
