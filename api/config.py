import sys
import logging

def load_configurations(app):
    app.config["ACCESS_TOKEN"] = "EAAVkCDn8mhwBOyUrtXQn0yJsd3GKEggxbw8QqKtqt8qzSxFZBYHn8s7N8I65RbHvv0pXLLhh5TJNQ6qqgOIS289stvq6i95bHolnX6GftBkZBqRPT3OoZBdTQo7BSwiHJQsDmS8ZBLzOnxmF4VsqHdz9CtE89ReBajjbjv56qLt9M0bmZAw6aYbnItlUHaBiF"
    app.config["APP_ID"] = "1517361378925084"
    app.config["APP_SECRET"] = "ba1fa5a0d87d3161d6a6556c71252345"
    app.config["RECIPIENT_WAID"] = "6281278989888"
    app.config["VERSION"] = "v21.0"
    app.config["PHONE_NUMBER_ID"] = "520078131183551"
    app.config["VERIFY_TOKEN"] = "jakeisadog"

def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )
