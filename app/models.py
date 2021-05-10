from app import db
from datetime import datetime


class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    currency = db.Column(db.String(64))
    summ = db.Column(db.Integer)
    send_time = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(140))


