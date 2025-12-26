import os
import pytz

TIMEZONE = pytz.timezone("Asia/Ho_Chi_Minh")

GROUP_ID = int(os.getenv("GROUP_ID"))
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", 0.65))

TIME_SLOTS = {
    "morning": ("06:00", "08:00"),
    "noon": ("11:30", "13:00"),
    "evening": ("17:30", "19:00")
}
