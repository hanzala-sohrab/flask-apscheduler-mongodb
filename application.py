from apscheduler.schedulers.base import BaseScheduler
import waapis
import project_secrets

from flask import Flask, request
from flask_pymongo import PyMongo
from apscheduler.jobstores.base import JobLookupError
from datetime import datetime, timedelta
from pymongo.errors import DuplicateKeyError
from pymongo.mongo_client import MongoClient
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor


application = Flask(__name__)

# Database config
application.config["MONGO_URI"] = project_secrets.MONGO_URI
mongo = PyMongo(application)
client = MongoClient(project_secrets.MONGO_URI)
db_operations = mongo.db.testing

jobstores = {
    'default': MongoDBJobStore(database='apscheduler', collection='jobs', client=client)
}
executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}

scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)
scheduler.start()

def sched(phone, lead, _name, _timestamp, i):
    if not lead['stop']:
        text = f"M{i} - Sent on {_timestamp}"
        print(text)
        resp = waapis.send_message(phone=phone, message=text)
        print(resp)

# def sched(_timestamp, i):
#     text = f"M{i} - Sent on {_timestamp}"
#     print(text)

@application.route('/webhook', methods=['POST'])
def webhook():
    data = request.json['messages'][0]
    if not data['fromMe']:
        phone = data['chatId'][:-5]
        _name = data['senderName'].strip()
        # email = request.json['email']

        # Phone number validation
        if len(phone) > 10:
            phone = phone[-10:]
        
        phone = "91" + phone

        lead = db_operations.find_one({'_id': int(phone)})
        _timestamp = datetime.now() + timedelta(seconds=10)
        if lead is None:
            new_lead = {'_id': int(phone), 'name': _name, "timestamp": round(_timestamp.timestamp()), 'ack': "", 'stop': False, 'jobs': []}
            db_operations.insert_one(new_lead)
            lead = db_operations.find_one({'_id': int(phone)})
        else:
            _update = {
                "$set": {
                    "stop": True
                }
            }
            db_operations.update_one(lead, _update)
        jobs = []
        r = scheduler.add_job(func=sched, trigger='date', args=[phone, lead, _name, _timestamp, 1], run_date=_timestamp, misfire_grace_time=5)
        print(r.id)
        jobs.append(r.id)
        _timestamp += timedelta(minutes=1)
        r = scheduler.add_job(func=sched, trigger='date', args=[phone, lead, _name, _timestamp, 2], run_date=_timestamp, misfire_grace_time=5)
        print(r.id)
        jobs.append(r.id)
        _timestamp += timedelta(minutes=1)
        r = scheduler.add_job(func=sched, trigger='date', args=[phone, lead, _name, _timestamp, 3], run_date=_timestamp, misfire_grace_time=5)
        print(r.id)
        jobs.append(r.id)
        _update = {
            "$set": {
                "jobs": jobs
            }
        }
        db_operations.update_one(lead, _update)

    return {"message": "success"}


@application.route("/stop", methods=["POST"])
def stop():
    data = request.json
    phone = data['phone']
    # Phone number validation
    if len(phone) > 10:
        phone = phone[-10:]
    
    phone = "91" + phone

    lead = db_operations.find_one({'_id': int(phone)})
    
    for job in lead['jobs']:
        try:
            scheduler.pause_job(job_id=job)
        except JobLookupError:
            pass

    return {"message": "success"}


# @application.route("/")
# def home():
#     _timestamp = datetime.now() + timedelta(seconds=10)

#     r = scheduler.add_job(func=sched, trigger='date', args=[_timestamp, 1], run_date=_timestamp, misfire_grace_time=5)
#     print(r)
#     _timestamp += timedelta(minutes=1)
#     r = scheduler.add_job(func=sched, trigger='date', args=[_timestamp, 2], run_date=_timestamp, misfire_grace_time=5)
#     print(r)
#     _timestamp += timedelta(minutes=1)
#     r = scheduler.add_job(func=sched, trigger='date', args=[_timestamp, 3], run_date=_timestamp, misfire_grace_time=5)
#     print(r)

#     scheduler.print_jobs(jobstore=jobstores['default'])

#     return {"message": "success"}


if __name__ == '__main__':
    application.run(port=8000, debug=True)
