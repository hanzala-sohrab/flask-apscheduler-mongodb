import os
import json
import requests
import project_secrets

# API_URL = os.getenv("API_URL")
# TOKEN = os.getenv("TOKEN")
API_URL = project_secrets.API_URL
TOKEN = project_secrets.TOKEN

def send_message(phone, message):
    url = f"{API_URL}sendMessage?token={TOKEN}"
    headers = {'Content-type': 'application/json'}
    data = {
        "body": message,
        "phone": phone
    }
    data = json.dumps(data)

    resp = requests.post(url=url, headers=headers, data=data)


def send_file(phone, body, filename, caption):
    url = f"{API_URL}sendFile?token={TOKEN}"
    headers = {'Content-type': 'application/json'}
    data = {
        'body': body,
        'filename': filename,
        'caption': caption,
        'phone': phone
    }
    data = json.dumps(data)

    resp = requests.post(url=url, headers=headers, data=data)


def send_link(phone, body, previewBase64, title, text):
    url = f"{API_URL}sendLink?token={TOKEN}"
    headers = {'Content-type': 'application/json'}
    data = {
        'body': body,
        'previewBase64': previewBase64,
        'title': title,
        'text': text,
        'phone': phone
    }
    data = json.dumps(data)

    resp = requests.post(url=url, headers=headers, data=data)


if __name__ == '__main__':
    print("WhatsApp APIs")
