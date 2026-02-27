# redis_consumer.py
import os
import json
import redis
import threading
from ingestion import process_document_job

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
STREAM_NAME = "ingestion_stream"
GROUP_NAME = "workers"
CONSUMER_NAME = os.getenv("WORKER_NAME", "worker-1")

r = redis.Redis(host=REDIS_HOST, decode_responses=True)


def ensure_group():
    try:
        r.xgroup_create(STREAM_NAME, GROUP_NAME, id="0", mkstream=True)
    except redis.exceptions.ResponseError:
        pass  # группа уже существует


def consume():
    ensure_group()

    while True:
        messages = r.xreadgroup(
            GROUP_NAME,
            CONSUMER_NAME,
            {STREAM_NAME: ">"},
            count=5,
            block=5000
        )

        for stream, events in messages:
            for event_id, data in events:
                try:
                    payload = json.loads(data["data"])
                    process_document_job(payload)

                    # подтверждаем обработку
                    r.xack(STREAM_NAME, GROUP_NAME, event_id)

                except Exception as e:
                    print("Job failed:", e)
                    # можно добавить retry / DLQ