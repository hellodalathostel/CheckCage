from firebase import db
from datetime import datetime, timedelta
from config import TIMEZONE, TIME_SLOTS

def report_today():
    today = datetime.now(TIMEZONE).strftime("%Y-%m-%d")
    docs = db.collection("attendance").where("date", "==", today).stream()

    result = {slot: [] for slot in TIME_SLOTS}
    for d in docs:
        result[d.to_dict()["slot"]].append(d.to_dict()["full_name"])

    return result

def report_week():
    start = datetime.now(TIMEZONE) - timedelta(days=6)
    dates = [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
    docs = db.collection("attendance").where("date", "in", dates).stream()

    stats = {}
    for d in docs:
        name = d.to_dict()["full_name"]
        stats[name] = stats.get(name, 0) + 1

    return stats
