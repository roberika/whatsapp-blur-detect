from flask import Flask
import cv2
import pymupdf

app = Flask(__name__)
image_dpi = 72
image_size_landscape = (1200, 1600)
image_size_portrait = (1600, 1200)
blur_threshold = 100 # for now

@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/about')
def about():
    return 'About'

def variance_of_laplacian(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    height, width, _ = gray.shape
    if height > width:
        resized = cv2.resize(gray, image_size_portrait)
    else 
        resized = cv2.resize(gray, image_size_landscape)
    return cv2.Laplacian(resized, cv2.CV_64F).var()

def is_blur(image):
    fm = variance_of_laplacian(image)
    return True if fm >= blur_threshold else False

def webhook():
    # WhatsApp logic to get media
    #####
    # If it is a PDF file
    if(False):
        ##### Load the document
        doc = file
        for i in range(0, doc.page_count()):
            page = doc.load_page(i)
            pixmap = page.get_pixmap(dpi=image_dpi)
            image = pixmap.tobytes()
            if is_blur(image):
                ##### Send message
            else:
                ##### Send other message
    # If it is a JPEG or PNG file
    else:
        ##### Load the image
        image = file
        if is_blur(image):
            ##### Send message
        else:
            ##### Send other message
