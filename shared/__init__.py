import os
from datetime import datetime


def get_config():
    return {
        "TOURNAMENT_REGISTRATION_CUTOFF": datetime.fromisoformat(
            os.environ.get("TOURNAMENT_REGISTRATION_CUTOFF"),
        ),
        "MAX_ENTRIES_PER_DAY": int(os.environ.get("MAX_ENTRIES_PER_DAY", 3)),
        "DEBUG": os.environ.get("DEBUG", False) == "TRUE",
        "FFTT_SERIAL_NO": os.environ.get("FFTT_SERIAL_NO"),
        "FFTT_APP_ID": os.environ.get("FFTT_APP_ID"),
        "FFTT_PASSWORD": os.environ.get("FFTT_PASSWORD"),
    }
