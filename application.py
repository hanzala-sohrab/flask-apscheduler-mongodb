import waapis
import project_secrets

from flask import Flask, request
from flask_pymongo import PyMongo
from datetime import datetime, timedelta
from pymongo.errors import DuplicateKeyError
from pymongo.mongo_client import MongoClient
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.schedulers.background import BackgroundScheduler


application = Flask(__name__)

# Database config
application.config["MONGO_URI"] = project_secrets.MONGO_URI
mongo = PyMongo(application)
client = MongoClient(project_secrets.MONGO_URI)
db_operations = mongo.db.testing

jobstores = {
    'default': MongoDBJobStore(database='apscheduler', collection='jobs', client=client)
}

scheduler = BackgroundScheduler(jobstores=jobstores)
scheduler.start()

def sched(phone, lead, _name, _timestamp):
    text = f"Sent on {_timestamp}"
    resp = waapis.send_message(phone=phone, message=text)
    print(resp)

@application.route('/webhook', methods=['POST'])
def webhook():
    data = request.json['messages'][0]
    phone = data['chatId'][:-5]
    _name = data['senderName'].strip()
    # email = request.json['email']

    # Phone number validation
    if len(phone) > 10:
        phone = phone[-10:]
    
    phone = "91" + phone

    lead = db_operations.find_one({'_id': int(phone)})
    if lead is None:
        try:
            _timestamp = datetime.now() + timedelta(seconds=10)
            new_lead = {'_id': int(phone), 'name': _name, "timestamp": round(_timestamp.timestamp()), 'ack': ""}
            db_operations.insert_one(new_lead)
            lead = db_operations.find_one({'_id': int(phone)})
            r = scheduler.add_job(func=sched, trigger='date', args=[phone, lead, _name, _timestamp], run_date=_timestamp)
            print(r)
            _timestamp += timedelta(minutes=3)
            r = scheduler.add_job(func=sched, trigger='date', args=[phone, lead, _name, _timestamp], run_date=_timestamp)
            print(r)
            _timestamp += timedelta(minutes=2)
            r = scheduler.add_job(func=sched, trigger='date', args=[phone, lead, _name, _timestamp], run_date=_timestamp)
            print(r)
        except DuplicateKeyError:
            pass

    return {"message": "success"}

if __name__ == '__main__':
    application.run(port=8000)
