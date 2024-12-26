import sys
import logging

def load_configurations(app):
    app.config["ACCESS_TOKEN"] = "EAAVkCDn8mhwBO3o1DV28vQfjksG13nOGRgTptuBoLKxNNZCGrvVgWiMFgZCZCs4ZAYAVPVNAY6W926CS9g2LnfXWLKZAKM5q9COJNuipeNQd56YCG4dZB1QhxdkX2WdimzgGlEIFFDdvnVd5P48jUBp3rzTkq1IqJZB7LdfA96wzimH5Kh6qZAzZAn1w0ogo5aRwP"
    app.config["APP_ID"] = "1517361378925084"
    app.config["APP_SECRET"] = "ba1fa5a0d87d3161d6a6556c71252345"
    app.config["RECIPIENT_WAID"] = "6281278989888"
    app.config["VERSION"] = "v21.0"
    app.config["PHONE_NUMBER_ID"] = "510340225497619"
    app.config["VERIFY_TOKEN"] = "jakeisadog"

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )
