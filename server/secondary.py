from flask import Flask, request, jsonify
import time
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

replicated_messages = set()

@app.route('/replicate', methods=['POST'])
def replicate_message():
    data = request.json
    message = data.get('message')

    sleep_time = int(os.environ.get("SLEEP_TIME", 30))
    time.sleep(sleep_time)

    if message in replicated_messages:
        logging.warning(f"Duplicate message received: {message}. Ignoring.")
        return jsonify({"status": "Duplicate message received"}), 400

    replicated_messages.add(message)  # Add to set for deduplication
    logging.info(f"Received message for replication: {message}")

    return jsonify({"status": "Message received"}), 200

@app.route('/messages', methods=['GET'])
def get_replicated_messages():
    logging.info("Retrieving replicated messages")
    return jsonify({"replicated_messages": list(replicated_messages)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5002))
    app.run(host='0.0.0.0', port=port)
