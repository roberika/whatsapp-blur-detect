from flask import Flask, request
import logging
from api.config import load_configurations, configure_logging
from .views import webhook_blueprint
from .utils.whatsapp_utils import process_image

def create_app():
    app = Flask(__name__)

    # Load configurations and logging settings
    load_configurations(app)
    configure_logging()

    # Import and register blueprints, if any
    app.register_blueprint(webhook_blueprint)

    return app

app = create_app()

if __name__ == "__main__":
    logging.info("Flask app started")
    app.run(host="0.0.0.0", port=8000)

@app.route('/')
def home():
    return 'Hello, World!'

@app.route("/stress-test", methods=["GET"])
def ping():
    return 'Yup'

@app.route("/stress-test", methods=["POST"])
def stress_test():
    process_image(request.files["image"])
    return