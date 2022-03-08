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

# Если модифицируете эти обзоры, удалите файл token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.modify']



def get_service():
    # Файл token.json хранит доступ пользователя и обновлять токены, и это
    # создается автоматически при завершении потока авторизации для первого
    # время.
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))
    return service


def list_messages(service, user, query=''):
    """Получает список сообщений.

  Args:
    service: Уполномоченный экземпляр услуг API Gmail API.
    user: Адрес электронной почты учетной записи.
    query: Строка, используемая для фильтрации сообщений, возвращенных.
           Например.- 'label:UNREAD' только для непрочитанных сообщений.

  Returns:
    Список сообщений, соответствующих критериям запроса. Обратите внимание, что то
    Возвращенный список содержит идентификаторы сообщений, вы должны использовать Get с
    подходящий идентификатор, чтобы получить детали сообщения.
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
    """Получить сообщение и использовать его для создания сообщения MIME.

     Args:
       service: Уполномоченный экземпляр службы API Gmail.
       user_id: Адрес электронной почты пользователя. Специальное значение «я»
       возможно используется для обозначения аутентифицированного пользователя.
       msg_id: Идентификатор сообщения требуется.

     Returns:
       A MIME Message, consisting of data from Message.
     """
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id, format='full').execute()

        # print(f"Message snippet: {message['snippet']}")

        return message
    except errors.HttpError as error:
        print(f"An error occurred: {error}")



def sms_notification(msg_text):
    """Получить смс опевещение об интересующих изменениях в почтовом ящике"""
    
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
        """По дефолту мы настроенны на оповещения из портала электронное правосудие, а точнее,
        как только дело в котором вы принимаем участие, хоть как то изменилось,
        мгновенно отправляется смс с кратким описанием изменений и ссылками для быстрого перехода
        к ним - без необходимости тратить время на отслеживание и переходы по разделам.
        Что в связи с априори сильной загруженностью среднестатистического юриста, 
        ведушего минимум 15-20 дел одновременн - экономит для него, около 1 часа рабочего времени в день !
        """
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
