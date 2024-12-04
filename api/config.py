import sys
import logging

def load_configurations(app):
    app.config["ACCESS_TOKEN"] = "EAAVkCDn8mhwBOyIW5pZCXTEVSYcg7U7ELHdnP3zOsvpUXG908L4sUoSJnxlt69mSx0CmaoiqZBLJ8eB688JminXZAhCuCGbZAR48jdhI39XZBimYCFye7aDbZAuTlTisLtRnhQvhhl6JZCQZBeCNzcBgEFUOU6ueWVFWJoqIIFZApMlTKEBim5WKGk340V7iHQSUWWTzuWsHFBy3NGWQpN8vcOMndnTMZD"
    app.config["APP_ID"] = "1517361378925084"
    app.config["APP_SECRET"] = "ba1fa5a0d87d3161d6a6556c71252345"
    app.config["RECIPIENT_WAID"] = "6281278989888"
    app.config["VERSION"] = "v18.0"
    app.config["PHONE_NUMBER_ID"] = "520078131183551"

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )
