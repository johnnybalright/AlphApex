import os
import json
from fastapi import FastAPI, Form
import requests
import sqlite3
import time
from dotenv import load_dotenv
import uuid
import redis
from redis import Redis
from rq import Queue
from loggers.logger import setup_logger

load_dotenv(
    "/home/jpournelle/python_projects/plabz/river_division/main/main.env"
    )

logger = setup_logger(__name__, __name__)

r = redis.Redis(
  host='redis-13920.c267.us-east-1-4.ec2.cloud.redislabs.com',
  port=13920,
  password='12PqdVesu1jggRJXFdq02gnWmDenaxup')

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}


@app.post("/webhook")
async def webhook(id: str = Form(...), parcelid: str = Form(...),
                  fname: str = Form(...), lname: str = Form(...),
                  email: str = Form(...), phone: str = Form(...),
                  oaddr1: str = Form(...), ocity: str = Form(...),
                  ostate: str = Form(...), ozipcd: str = Form(...),
                  project: str = Form(...), phyaddr1: str = Form(...),
                  phycity: str = Form(...), phyzip: str = Form(...),
                  cntyname: str = Form(...), decklength: str = Form(...),
                  deckwidth: str = Form(...), gangwaylength: str = Form(...),
                  gangwaywidth: str = Form(...), docklength: str = Form(...),
                  dockwidth: str = Form(...), handrailheight: str = Form(...)):
    hash_data = {
        'fname': f'{fname}',
        'lname': f'{lname}',
        'id': f'{id}',
        'phone': f'{phone}',
        'email': f'{email}',
        'parcelid': f'{parcelid}',
        'oaddr1': f'{oaddr1}',
        'ocity': f'{ocity}',
        'ostate': f'{ostate}',
        'ozipcd': f'{ozipcd}',
        'phyaddr1': f'{phyaddr1}',
        'phycity': f'{phycity}',
        'phyzip': f'{phyzip}',
        'cntyname': f'{cntyname}',
        'decklength': f'{decklength}',
        'deckwidth': f'{deckwidth}',
        'gangwaylength': f'{gangwaylength}',
        'gangwaywidth': f'{gangwaywidth}',
        'docklength': f'{docklength}',
        'dockwidth': f'{dockwidth}',
        'handrailheight': f'{handrailheight}',
        'project': f'{project}'
        }
    url = os.getenv("SLACK_URL")
    headers = {"Content-Type": "application/json"}
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    slack_message = {
        "text": "AlphApex Floodway Program initiated for " \
            + f"project {lname}-{id} at {current_time}."
    }
    requests.post(url, json=slack_message, headers=headers)
    if not id == None:
        pipeline = r.pipeline()
        task_name = uuid.uuid4()
        task_id = str(task_name)
        pipeline.hmset(
            str(task_id),
            {"payload": json.dumps(hash_data),
             "status": "pending"}
            )
        pipeline.lpush("task_todo", str(task_id))
        pipeline.execute()
