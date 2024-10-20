import os


class Config(object):
    TG_BOT_TOKEN = os.environ.get("7137946160:AAEtwG3rYA9WwtWCUNsSVxERMPDJVrke-DE", "7013440973")

    APP_ID = int(os.environ.get("APP_ID", 21669021))

    API_HASH = os.environ.get("API_HASH", "bcdae25b210b2cbe27c03117328648a2")
