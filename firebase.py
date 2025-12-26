import firebase_admin
from firebase_admin import credentials, firestore
import base64
import json
import os

encoded = os.getenv("FIREBASE_CREDENTIALS_BASE64")
decoded = base64.b64decode(encoded).decode("utf-8")

cred = credentials.Certificate(json.loads(decoded))
firebase_admin.initialize_app(cred)

db = firestore.client()
