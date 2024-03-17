import datetime
import json
import logging
import os
import time

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from telegram import send_message

logging.basicConfig(format='%(asctime)s [%(levelname)s] %(message)s',
                    level=logging.INFO, handlers=[logging.StreamHandler()])

# telegram chat IDs
BOT_TOKEN = "<TELEGRAM_BOT_TOKEN>"
CHAT_ID = "<CHAT_ID>"

# user account
GROUP_ID = "19123123"
APPOINTMENT_ID = "44123123"

USER = "<EMAIL>"
PASSWORD = "<PASSWORD>"


def format_time_rfc3339(_self, record, _datefmt=None):
    return (
        datetime.datetime.fromtimestamp(record.created, datetime.timezone.utc)
        .astimezone()
        .isoformat()
    )


logging.Formatter.formatTime = format_time_rfc3339


# iso date format with milliseconds
# set logger formatting
# formatter = logging.Formatter('%(asctime)s:%(name)s:%(message)s')

def login(driver, user, password):
    url = "https://ais.usvisa-info.com/en-gb/niv/users/sign_in"
    driver.get(url)
    driver.find_element(By.CSS_SELECTOR, "#user_email").send_keys(user)
    driver.find_element(By.CSS_SELECTOR, "#user_password").send_keys(password)
    driver.find_element(By.XPATH, '//*[@id="sign_in_form"]/div[3]/label').click()
    driver.find_element(By.XPATH, '//*[@id="sign_in_form"]/p[1]/input').click()
    time.sleep(5)


def get_appointment(driver, appointment_id):
    url = f'https://ais.usvisa-info.com/en-gb/niv/schedule/{appointment_id}/appointment'
    driver.get(url)
    driver.get(
        f"https://ais.usvisa-info.com/en-gb/niv/schedule/{appointment_id}"
        f"/appointment/days/17.json?appointments[expedite]=false")
    raw_data = driver.find_element(By.TAG_NAME, "pre").text
    logging.info(f"loaded appointments: {raw_data}")
    appointments = json.loads(raw_data)
    return appointments


def get_current_appointment(driver, group_id, _appointment_id):
    url = f"https://ais.usvisa-info.com/en-gb/niv/groups/{group_id}"
    driver.get(url)
    existing_appointments = driver.find_elements(By.CSS_SELECTOR, '.consular-appt')
    logging.info(f"existing appointments: {len(existing_appointments)}")
    raw_date = existing_appointments[0].text[len("Consular Appointment: "):]
    truncated_date = " ".join(raw_date.strip().split(" ")[0:4])
    logging.info(f"parsing appointment: {truncated_date}")
    # parse "25 January, 2023, 09:00"
    date = datetime.datetime.strptime(truncated_date, "%d %B, %Y, %H:%M")
    logging.info(f"latest appointment date: {date}")
    return date


def main():
    logging.info("Started")
    group_id = os.environ.get("GROUP_ID", GROUP_ID)
    user = os.getenv("APP_USER", USER)
    password = os.getenv("APP_PASSWORD", PASSWORD)
    appointment_id = os.getenv("APPOINTMENT_ID", APPOINTMENT_ID)

    url = f"https://ais.usvisa-info.com/en-ir/niv/groups/{group_id}"
    chrome = '/usr/lib/chromium-browser/chromedriver'
    if os.path.exists(chrome):
        display = Display(visible=False, size=(1600, 800))
        display.start()
        driver = webdriver.Chrome()
    else:
        driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(url)
    login(driver, user, password)
    current_date = get_current_appointment(driver, group_id, appointment_id)
    retry = 3
    sleep_minutes = 2
    for i in range(retry):
        logging.info(f"Checking for new appointments, attempt {i}/{retry}")
        appointments = get_appointment(driver, appointment_id)
        if len(appointments) == 0:
            logging.warning("no appointments found")
        else:
            first_date = appointments[0]["date"]
            message = f"found {len(appointments)} appointments, first date: {first_date}"
            first_date = datetime.datetime.strptime(first_date, "%Y-%m-%d")
            logging.info(message)
            if first_date > current_date:
                logging.info(
                    f"first date {first_date} is after the current date {current_date}, not sending notification")
            else:
                logging.info(f"first date {first_date} is before the current date {current_date}, sending notification")
                send_message(BOT_TOKEN, CHAT_ID, message)
        if i < retry - 1:
            logging.info(f"sleeping for {sleep_minutes} minutes")
            time.sleep(sleep_minutes * 60)
    logging.info("Finished")


if __name__ == '__main__':
    main()
