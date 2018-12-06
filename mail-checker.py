#!/env/bin/python3.7
#
#
from __future__ import print_function

from doctest import _exception_traceback

from twilio.rest import Client
from apiclient import errors
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import time

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.modify']


# ФУНКЦИЯ АУТИНТИФИКАЦИИ
def get_service():
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))
    return service


# ПОЛУЧАЕМ СПИСОК СООБЩЕНИЙ
def list_messages(service, user, query=''):
    """Gets a list of messages.

  Args:
    service: Authorized Gmail API service instance.
    user: The email address of the account.
    query: String used to filter messages returned.
           Eg.- 'label:UNREAD' for unread Messages only.

  Returns:
    List of messages that match the criteria of the query. Note that the
    returned list contains Message IDs, you must use get with the
    appropriate id to get the details of a Message.
  """
    try:
        response = service.users().messages().list(userId=user, q=query).execute()
        messages = response['messages']

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId=user, q=query,
                                                       pageToken=page_token).execute()
            messages.extend(response['messages'])

        return messages

    except:
        return


# ПОЛУЧАЕМ ДАННЫЕ КАЖДОГО СООБЩЕНИЯ
def read_message(service, user_id, msg_id):
    """Get a Message and use it to create a MIME Message.

     Args:
       service: Authorized Gmail API service instance.
       user_id: User's email address. The special value "me"
       can be used to indicate the authenticated user.
       msg_id: The ID of the Message required.

     Returns:
       A MIME Message, consisting of data from Message.
     """
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id, format='full').execute()

        # print(f"Message snippet: {message['snippet']}")

        return message
    except errors.HttpError as error:
        print(f"An error occurred: {error}")


# ФУНКЦИЯ ОТПРАВКИ СМС
def sms_notification(msg_text):
    account_sid = 'AC669d9811cff3e651b8525e353bba5078'
    auth_token = '1ce7bce90364b673bb7a1683e1bd0222'

    sms_client = Client(account_sid, auth_token)

    sms = sms_client.messages \
        .create(
        body=msg_text,
        from_="+18544005478",
        to="+79214447344"
    )

    sms.sid


if __name__ == '__main__':
    message_box = list()
    try:
        service = get_service()
        mess_list = list_messages(service, 'me', 'in:anywhere from:guard@arbitr.ru is:unread')
        for message in mess_list:
            msg = read_message(service, 'me', message['id'])
            message_box.append(msg)

        if len(message_box) > 0:
            for msg in message_box:
                sms_notification(msg['snippet'])
        else:
            print(f"Ничего не происходит")
    except Exception as e:
        print(f"{e.__class__.__name__} : {e.args}")
