import os
import asyncio
import time
from fastapi import FastAPI, HTTPException
import httpx

from src.model.model import ReplicationRequest
from src.utils.logger import get_logger

app = FastAPI()

messages = []
sequence_id = 0

SECONDARIES = os.environ.get("SECONDARIES", "").split(',')

secondary_health = {secondary: "Unknown" for secondary in SECONDARIES}

HEALTH_CHECK_INTERVAL = 10
SUSPECTED_THRESHOLD = 3

shutdown_signal = asyncio.Event()

logger = get_logger(__name__)


async def replicate_to_secondary(secondary, message):
    timeout_config = httpx.Timeout(10.0, read=None)
    async with httpx.AsyncClient(timeout=timeout_config) as client:
        for attempt in range(3):
            try:
                response = await client.post(f"{secondary}/replicate/", json={"content": message})
                if response.status_code == 200:
                    logger.info(f"Replication to {secondary} was successful.")
                    return True
                else:
                    logger.warning(
                        f"Attempt {attempt + 1} to replicate to {secondary} returned status {response.status_code}.")
            except httpx.RequestError as ex:
                logger.error(f"Replication to {secondary} failed on attempt {attempt + 1} due to: {repr(ex)}.")
            await asyncio.sleep(1)
    logger.error(f"Replication to {secondary} failed after 3 attempts.")
    return False


@app.post("/")
async def post_message(replication_request: ReplicationRequest):
    global sequence_id

    max_write_concern = len(SECONDARIES) + 1
    if replication_request.write_concern > max_write_concern:
        raise HTTPException(
            status_code=400,
            detail=f"The specified write concern exceeds the maximum allowed, which is {max_write_concern}."
        )

    if any(msg.id == replication_request.message.id for msg in messages):
        logger.info(f"Duplicate message ID {replication_request.message.id} received, ignoring the request.")
        return {"status": "success", "detail": "Duplicate message, already replicated."}

    replication_request.message.queue_number = sequence_id
    sequence_id += 1
    messages.append(replication_request.message)

    if replication_request.write_concern == 1:
        logger.info("Write concern is set to 1, responding to the client without waiting for acknowledgments from secondaries.")
        for secondary in SECONDARIES:
            asyncio.create_task(replicate_to_secondary(secondary, replication_request.message.message))
        return {"status": "success", "detail": "Message replicated with write concern 1"}

    acks_needed = replication_request.write_concern - 1
    semaphore = asyncio.Semaphore(0)
    replication_tasks = []

    for secondary in SECONDARIES:
        task = asyncio.create_task(replicate_and_release(secondary, replication_request.message.message, semaphore))
        replication_tasks.append(task)

    successful_acks = 1  # Ack from the master is always considered received
    replication_timeout = 10  # seconds
    try:
        for _ in range(acks_needed):
            await asyncio.wait_for(semaphore.acquire(), timeout=replication_timeout)
            successful_acks += 1
    except asyncio.TimeoutError:
        logger.warning("Timeout reached while waiting for replication acknowledgments.")

    if successful_acks >= replication_request.write_concern:
        return {"status": "success",
                "detail": f"Message replicated with write concern {replication_request.write_concern}"}
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Write concern not met. Required: {replication_request.write_concern}, received: {successful_acks} ACKs."
        )


async def replicate_and_release(secondary, message, semaphore):
    success = await replicate_to_secondary(secondary, message)
    if success:
        semaphore.release()


@app.get("/")
async def get_messages():
    sorted_messages = sorted(messages, key=lambda msg: msg.queue_number)
    return sorted_messages


async def perform_health_check(secondary):
    start_time = time.time()
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{secondary}/health/")
        response_time = time.time() - start_time

        if response.status_code == 200 and response_time < SUSPECTED_THRESHOLD:
            return secondary, "Healthy"
        else:
            return secondary, "Suspected"
    except Exception as ex:
        logger.error(f"Health check failed for {secondary}: {str(ex)}")
        return secondary, "Unhealthy"


async def check_secondary_health():
    while not shutdown_signal.is_set():
        health_check_tasks = [perform_health_check(secondary) for secondary in SECONDARIES]
        health_check_results = await asyncio.gather(*health_check_tasks)

        for secondary, status in health_check_results:
            secondary_health[secondary] = status

        await asyncio.sleep(HEALTH_CHECK_INTERVAL)


@app.get("/health/")
async def health_check():
    return secondary_health


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(check_secondary_health())


@app.on_event("shutdown")
async def shutdown_event():
    shutdown_signal.set()
