import datetime
import os

import requests
import logging


def send_message(bot_token, chat_id, text):
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    parameters = {
        'chat_id': chat_id,
        'text': text
    }
    return requests.post(url, parameters)


def send_photo(bot_token, chat_id, photo_file):
    url = f'https://api.telegram.org/bot{bot_token}/sendPhoto'
    parameters = {
        'chat_id': chat_id
    }
    return requests.post(url, parameters, files={'photo': photo_file})


# get all active chats for bot
def get_chats(bot_token):
    raw_data = requests.get(f"https://api.telegram.org/bot{bot_token}/getUpdates").json()
    logging.info(f"loaded chats: {raw_data}")


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                        level=logging.INFO)

    try:
        send_message(BOT_TOKEN, CHAT_ID,
                     f"Sending test message for notification {datetime.datetime.now()}")
    except Exception as e:
        logging.exception(e)
