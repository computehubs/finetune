import requests
import os
import json
import logging
from datetime import datetime, timedelta
import threading

LOG = logging.getLogger("send_payload")

prevTime = datetime.now()

def send_payload_async(payload):
    global prevTime
    env = os.environ.get("CHUB_ENV", "dev")

    try:
        payload["projectId"] = os.environ.get("CHUB_PROJECT_ID", "anonymous")
        payload["userId"] = os.environ.get("CHUB_USER_ID", "anonymous")
        payload["timestamp"] = datetime.now().isoformat()
        if payload.get("eval_samples_per_second", None) != None:
            url = "https://train-status.computehubs.com/eval/payload"
            if env == "local":
                url = "https://da9b-83-136-182-39.ngrok-free.app/eval/payload"

            payload["eval_samples_per_second"] = float(payload["eval_samples_per_second"])
            payload["eval_steps_per_second"] = float(payload["eval_steps_per_second"])
            payload["eval_loss"] = float(payload["eval_loss"])
            payload["eval_runtime"] = float(payload["eval_runtime"])

            data = json.dumps(payload)
            r = requests.post(url, 
            data=data, headers={"Content-Type": "application/json", "X-CHUB-API-KEY": os.environ.get("CHUB_HTTP_TK")},)

            LOG.info(r.status_code)
            LOG.info(r.text)
        else:
            url = "https://train-status.computehubs.com/train/payload"
            if env == "local":
                url = "https://da9b-83-136-182-39.ngrok-free.app/train/payload"

            payload["epoch"] = float(payload.get("epoch", 0))
            payload["loss"] = float(payload["loss"])
            payload["grad_norm"] = float(payload["grad_norm"])
            payload["learning_rate"] = float(payload["learning_rate"])
            data = json.dumps(payload)
            r = requests.post(url, 
            data=data, headers={"Content-Type": "application/json", "X-CHUB-API-KEY": os.environ.get("CHUB_HTTP_TK")},)

            LOG.info(r.status_code)
            LOG.info(r.text)
    except Exception as e:
        LOG.error(f"Error sending payload: {e}")

def send_payload(payload):
    global prevTime
    time_difference = abs(datetime.now() - prevTime)
    if time_difference > timedelta(seconds=6) or payload.get("eval_samples_per_second", None) != None:
        threading.Thread(target=send_payload_async, args=(payload, )).start()
        prevTime = datetime.now()

def send_http_payload_async(payload):
    try:
        payload["projectId"] = os.environ.get("CHUB_PROJECT_ID", "anonymous")
        payload["userId"] = os.environ.get("CHUB_USER_ID", "anonymous")
        payload["timestamp"] = datetime.now().isoformat()

        env = os.environ.get("CHUB_ENV", "dev")
        url = "https://train-status.computehubs.com/train/status"
        if env == "local":
            url = "https://da9b-83-136-182-39.ngrok-free.app/train/status"

        LOG.info(f"Sending payload: {payload}")

        data = json.dumps(payload)
        r = requests.post(url, 
        data=data, headers={"Content-Type": "application/json", "X-CHUB-API-KEY": os.environ.get("CHUB_HTTP_TK")})

        LOG.info(r.status_code)
        LOG.info(r.text)
    except Exception as e:
        LOG.error(f"Error sending payload: {e}")

def send_http_payload(payload):
    threading.Thread(target=send_http_payload_async, args=(payload, )).start()