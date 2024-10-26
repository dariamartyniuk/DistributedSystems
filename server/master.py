import asyncio

import aiohttp
from flask import Flask, request, jsonify

app = Flask(__name__)

SECONDARIES = ["http://secondary1:5001", "http://secondary2:5002", "http://secondary3:5003"]

async def replicate_message(session, secondary_url, message):
    try:
        async with session.post(f"{secondary_url}/replicate", json={"message": message}) as response:
            return response.status == 200
    except Exception as e:
        print(f"Error replicating to {secondary_url}: {e}")
        return False

@app.route("/send", methods=["POST"])
async def send_message():
    data = request.json
    message = data.get("message")
    write_concern = data.get("w", 1)

    acks_received = 0
    tasks = []

    async with aiohttp.ClientSession() as session:
        acks_received += 1

        tasks = [replicate_message(session, secondary_url, message) for secondary_url in SECONDARIES]

        for task in asyncio.as_completed(tasks):
            success = await task
            if write_concern == 1:
                break
            if success:
                acks_received += 1
            if acks_received >= write_concern:
                break

        if acks_received >= write_concern:
            return jsonify({"acks_received": acks_received, "status": "Message replicated successfully"})
        else:
            return jsonify({"acks_received": acks_received, "status": "Not enough acks received"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
