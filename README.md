# flask-apscheduler-mongodb

## Pausing some specific jobs
Provide the phone number of the user for whom, the job(s) is/are required to be paused.
- POST: /stop
- Payload
```json
{
    "phone": "919XXXXXXXXX"
}
```
- Response
```json
{
    "message": "success"
}
```
