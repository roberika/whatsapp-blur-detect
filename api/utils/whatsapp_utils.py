import logging
from flask import current_app, jsonify
import json
import requests
import re
from cv2 import cvtColor, COLOR_BGR2GRAY, resize, Laplacian, CV_64F, imdecode
import numpy as np
import pymupdf
from .reply_messages import (
    reply_text, reply_unknown,
    reply_document_blur, reply_document_clear,
    reply_image_blur, reply_image_clear,
    reply_document_blur_too_long, reply_document_clear_too_long,
)

def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Headers: {response.headers}")
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

image_dpi = 96 # mengikuti DPI gambar dari WhatsApp
image_size = 1600
blur_threshold = 39.71 # https://colab.research.google.com/drive/1gkUsybQlNrhDQhLNg0pAwnqINuNSqRvk?usp=sharing

def variance_of_laplacian(image):
    return Laplacian(image, CV_64F).var()

def is_blur(image):
    height, width, _ = image.shape
    gray = cvtColor(image, COLOR_BGR2GRAY)
    if height <= width:
        resized = resize(gray, (image_size, int(image_size * height / width)))
    else:
        resized = resize(gray, (int(image_size * width / height), image_size))
    fm = variance_of_laplacian(resized)
    logging.info(f"Focus Measure: {fm}")
    return True if fm <= blur_threshold else False

def generate_response(message):
    if is_valid_image_message(message):
        return identify_blur(message["image"]["id"])
    if is_valid_document_message(message):
        return identify_blur(message["document"]["id"])
    if is_valid_text_message(message):
        return reply_text()
    return reply_unknown()

def identify_blur(media_id):
    data, mime_type = download_media(media_id)
    # If it is a PDF file
    if (mime_type == 'application/pdf'):
        under_50, blur_pages = process_document(data)
        if under_50:
            if blur_pages:
                return reply_document_blur(blur_pages)
            else:
                return reply_document_clear()
        else:
            if blur_pages:
                return reply_document_blur_too_long(blur_pages)
            else:
                return reply_document_clear_too_long()
    # If it is an image type file
    elif ('image' in mime_type):
        if process_image(data):
            return reply_image_blur()
        else:
            return reply_image_clear()
    return reply_unknown()

# Returns on what pages the image is blurred in
def process_document(data):
    doc = pymupdf.Document(stream=data)
    blur_pages = []
    pages = doc.page_count
    for i in range(0, min(pages, 50)):
        page = doc.load_page(i)
        pixmap = page.get_pixmap(dpi=image_dpi)
        image = np.frombuffer(pixmap.samples_mv, dtype=np.uint8).reshape((pixmap.height, pixmap.width, -1))
        if is_blur(image):
            blur_pages.append(i+1)
    return (True if pages <= 50 else False), blur_pages

# Returns is the image blurred
def process_image(data):
    arr = np.asarray(bytearray(data), dtype=np.uint8)
    image = imdecode(arr, -1)
    return is_blur(image)

# Returns the image in a fucking header
def download_media(media_id):
    media_url, mime_type = retrieve_media_url(media_id)

    headers = {
        "Content-Type": mime_type,
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }

    url = media_url

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
        # Return the image
        logging.info(f"Status: {response.status_code}")
        logging.info(f"Headers: {response.headers}")
        logging.info(f"Content-type: {response.headers.get('content-type')}")
        logging.info(f"Media File: {True if (response.content and response.content != None) else False}")
        logging.info(f"Mime Type: {mime_type}")
        logging.info("Media downloaded")
        return response.content, mime_type


# Returns the url and mime type of the media
# https://github.com/shreyas-sreedhar/whatsapp-Cloudapi-aws-s3/blob/main/index.js
def retrieve_media_url(media_id):
    headers = {
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
        # Return the url
        url = response.json()['url']
        mime_type = response.json()['mime_type']
        log_http_response(response)
        logging.info(f"URL: {url}")
        logging.info(f"Mime Type: {mime_type}")
        logging.info("Media url retrieved")
        return url, mime_type


def send_message(data):
    headers = {
        "Content-Type": "application/json",
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

def is_valid_document_message(message):
    return (
        message.get('type')
        and message['type'] == 'document'
        and message['document'] 
    )

def is_valid_text_message(message):
    return (
        message["text"]
        and message['text']["body"]
    )