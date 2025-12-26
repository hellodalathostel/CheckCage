import firebase_admin
from firebase_admin import credentials, firestore
import json
import os

cred = credentials.Certificate(
    json.loads(os.getenv("FIREBASE_CREDENTIALS_JSON"))
)
firebase_admin.initialize_app(cred)

db = firestore.client()
