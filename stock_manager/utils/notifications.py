"""
Notification utility for Stock Management Application.

Provides methods for sending notifications via email to stock managers.
"""

import json
import logging
import smtplib
from email.message import EmailMessage

from PyQt5.QtWidgets import QMessageBox


def send_email(body: str) -> bool:
    """
    Sends a notification to the common stock project manager via email.

    :param body: message to be displayed in the database
    :return: `True` if the notification is sent successfully,
    `False` otherwise.
    """

    try:
        msg = EmailMessage()
        msg.set_content(body)
        msg['subject'] = 'Common Stock Notification'
        msg['to'] = 'lkingerslev@gmail.com'
        # TODO: replace with stock manager email

        f = open('../../assets/gmail_credentials.json')
        data: dict[str, str] = json.load(f)

        user = data['user']
        msg['from'] = user
        password = data['password']

        server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=20)
        server.login(user, password)

        server.send_message(msg)

        server.quit()
        return True
    except Exception as e:
        logging.getLogger().warning(f'Error Sending Email Notification: {e}')
        QMessageBox.warning(
            None,
            'Email Send Error',
            'Error Sending Email Notification'
        )
        return False
