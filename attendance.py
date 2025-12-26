from datetime import datetime
from config import TIMEZONE, TIME_SLOTS
from firebase import db

def get_current_slot():
    now = datetime.now(TIMEZONE).time()
    for slot, (start, end) in TIME_SLOTS.items():
        if start <= now.strftime("%H:%M") <= end:
            return slot
    return None

def already_checked(user_id, date, slot):
    doc_id = f"{date}_{user_id}_{slot}"
    return db.collection("attendance").document(doc_id).get().exists

def save_attendance(data):
    doc_id = f"{data['date']}_{data['user_id']}_{data['slot']}"
    db.collection("attendance").document(doc_id).set(data)
