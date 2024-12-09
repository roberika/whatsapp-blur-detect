import logging
from flask import current_app, jsonify
import json
import requests
import re
import cv2
import numpy as np
import pymupdf

def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    logging.info(f"Body: {response.text}")


def get_text_message_input(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )

image_dpi = 72
image_size_landscape = (1200, 1600)
image_size_portrait = (1600, 1200)
blur_threshold = 100 # for now

def variance_of_laplacian(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    height, width, _ = gray.shape
    if height > width:
        resized = cv2.resize(gray, image_size_portrait)
    else:
        resized = cv2.resize(gray, image_size_landscape)
    return cv2.Laplacian(resized, cv2.CV_64F).var()

def is_blur(image):
    fm = variance_of_laplacian(image)
    return True if fm >= blur_threshold else False

def generate_response(message):
    if is_valid_image_message(message):
        return identify_blur(message["image"]["id"])
    if is_valid_text_message(message):
        return message["text"]["body"].upper()
    return 'I don\'t understand what you\'re saying.'

def identify_blur(media_id):
    download_media(media_id)
#     # If it is a PDF file
#     if(file_type == 'document'):
#         req = download_media(media_id)
#         data = req.content
#         doc = pymupdf.Document(stream=data)
#         blur_pages = []
#         for i in range(0, doc.page_count()):
#             page = doc.load_page(i)
#             pixmap = page.get_pixmap(dpi=image_dpi)
#             image = pixmap.tobytes()
#             if is_blur(image):
#                 blur_pages.append(i+1)
#         if blur_pages:
#             return "Dokumen yang anda kirim memiliki blur pada halaman " + str(blur_pages)
#        else:
#             return "Dokumen yang anda kirim tidak memiliki blur"
#     # If it is a JPEG or PNG file
#     else:
#         req = download_media(media_id)
#         arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
#         image = cv2.imdecode(arr, -1)
#         if is_blur(image):
#             return "Gambar anda memiliki blur"
#         else:
#             return "Gambar anda tidak memiliki blur"
    return 'Hey, it\'s an image!'


def download_media(media_id):
    media_url = retrieve_media_url(media_id)

    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }

    url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{media_url}"

    try:
        response = requests.get(
            url, headers=headers, timeout=10
        )  # 10 seconds timeout as an example
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.Timeout:
        logging.error("Timeout occurred while downloading media")
        return jsonify({"status": "error", "message": "Request timed out"}), 408
    except (
        requests.RequestException
    ) as e:  # This will catch any general request exception
        logging.error(f"Request failed due to: {e}")
        return jsonify({"status": "error", "message": "Failed to download media"}), 500
    else:
        # Process the response as normal
        log_http_response(response)
        logging.info("Media downloaded")
        return response.json()


def retrieve_media_url(media_id):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }

    url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{media_id}"

    try:
        response = requests.get(
            url, headers=headers, timeout=10
        )  # 10 seconds timeout as an example
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.Timeout:
        logging.error("Timeout occurred while retrieving media url")
        return jsonify({"status": "error", "message": "Request timed out"}), 408
    except (
        requests.RequestException
    ) as e:  # This will catch any general request exception
        logging.error(f"Request failed due to: {e}")
        return jsonify({"status": "error", "message": "Failed to retrieve media url"}), 500
    else:
        # Process the response as normal
        log_http_response(response)
        logging.info("Media url retrieved")
        return response.json()['url']


def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }

    url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['PHONE_NUMBER_ID']}/messages"

    try:
        response = requests.post(
            url, data=data, headers=headers, timeout=10
        )  # 10 seconds timeout as an example
        response.raise_for_status()  # Raises an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.Timeout:
        logging.error("Timeout occurred while sending message")
        return jsonify({"status": "error", "message": "Request timed out"}), 408
    except (
        requests.RequestException
    ) as e:  # This will catch any general request exception
        logging.error(f"Request failed due to: {e}")
        return jsonify({"status": "error", "message": "Failed to send message"}), 500
    else:
        # Process the response as normal
        log_http_response(response)
        logging.info("Message sent")
        return response


def process_text_for_whatsapp(text):
    # Remove brackets
    pattern = r"\【.*?\】"
    # Substitute the pattern with an empty string
    text = re.sub(pattern, "", text).strip()

    # Pattern to find double asterisks including the word(s) in between
    pattern = r"\*\*(.*?)\*\*"

    # Replacement pattern with single asterisks
    replacement = r"*\1*"

    # Substitute occurrences of the pattern with the replacement
    whatsapp_style_text = re.sub(pattern, replacement, text)

    return whatsapp_style_text


def process_whatsapp_message(body):
    logging.info(body)
    wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
    name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]

    message = body["entry"][0]["changes"][0]["value"]["messages"][0]

    # TODO: implement custom function here
    response = generate_response(message)

    data = get_text_message_input(current_app.config["RECIPIENT_WAID"], response)
    send_message(data)


def is_valid_whatsapp_message(body):
    """
    Check if the incoming webhook event has a valid WhatsApp message structure.
    """
    return (
        body.get("object")
        and body.get("entry")
        and body["entry"][0].get("changes")
        and body["entry"][0]["changes"][0].get("value")
        and body["entry"][0]["changes"][0]["value"].get("messages")
        and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )

def is_valid_image_message(message):
    return (
        message.get('type')
        and message['type'] == 'image'
        and message['image'] 
    )

def is_valid_text_message(message):
    return (
        message["text"]
        and message['text']["body"]
    )