from flask import Flask
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from config import Config
from dotenv import load_dotenv
import os

load_dotenv('sendgrid.env')


def send_email(fromEmail, toEmail, subject, content):
    try:
        message = Mail(
        from_email=fromEmail,
        to_emails=toEmail,
        subject=subject,
        html_content=content)

        sg = SendGridAPIClient(os.getenv('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(str(e))