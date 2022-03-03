
from msilib.schema import Error
import os.path
from xml.etree.ElementInclude import include

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64

import  global_defs as gd
from global_defs import log


gmail_service = None

def get_gmail_service():
    global gmail_service
    if gmail_service is None:
        log.info("first time, will get new gmail service")
        gmail_service = get_gmail_service_native()

    return gmail_service


def get_gmail_service_native():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(gd.gmail_oauth_token_filepath):
        creds = Credentials.from_authorized_user_file(gd.gmail_oauth_token_filepath, gd.ALL_SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(gd.gmail_credentials_filepath, gd.ALL_SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(gd.gmail_oauth_token_filepath, 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        return service
    
    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        log.error(f'An error occurred: {error}')
    return None


def create_message(sender, to, subject, body):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

  Returns:
    An object containing a base64url encoded email object.
  """
  message = MIMEText(body)
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject
  # return {'raw': base64.urlsafe_b64encode(message.as_string())}
  return {'raw': message }



def build_message_OOOD(destination, obj, body, attachments=[]):
    if not attachments: # no attachments given
        message = MIMEText(body)
        message['to'] = gd.EMAIL_ENRICO200165
        message['from'] = gd.EMAIL_VIALI_GALILEI
        message['subject'] = obj
    else:
        message = MIMEMultipart()
        message['to'] = gd.EMAIL_ENRICO200165
        message['from'] = gd.EMAIL_VIALI_GALILEI
        message['subject'] = obj
        message.attach(MIMEText(body))
        # for filename in attachments:
        #     add_attachment(message, filename)
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}


def build_message(to, sender, obj, body, attachments=[]):
    if not attachments: # no attachments given
        message = MIMEText(body)
        message['to'] = gd.EMAIL_ENRICO200165
        message['from'] = gd.EMAIL_VIALI_GALILEI
        message['subject'] = obj
    else:
        message = MIMEMultipart()
        message['to'] = gd.EMAIL_ENRICO200165
        message['from'] = gd.EMAIL_VIALI_GALILEI
        message['subject'] = obj
        message.attach(MIMEText(body))
        # for filename in attachments:
        #     add_attachment(message, filename)
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}


# copiato da https://developers.google.com/gmail/api/guides/sending
def send_message(service, user_id, message):
  """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
  try:
    message = (service.users().messages().send(userId=user_id, body=message).execute())
    log.info('Message Id: %s' % message['id'])
    return message
  except :
    print('An error occurred: ')



def get_labels(gmail_service):
    """sample method from tutorial"""
    results = gmail_service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    if not labels:
        log.info('No labels found.')
        return
    log.info('--- Labels:')
    for label in labels:
        log.info("\n - "+label['name'])


def main():

    try:
        gmail_srv = get_gmail_service()
        # get_labels(gmail_srv)

        lines = ["uno","due","tre"]
        body = "\n".join(lines)
        msg = build_message(gd.EMAIL_VIALI_GALILEI, gd.EMAIL_ENRICO200165, 
            obj = "test, usato build message", body = body, attachments=[])
        send_message(service = gmail_srv, user_id = "me", message = msg)
        
    
    except Exception as e:
        log.error(e)

if __name__ == '__main__':
    main()