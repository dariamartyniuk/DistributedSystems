from flask import Flask, request, jsonify
import time

app = Flask(__name__)

replicated_messages = []

@app.route('/replicate', methods=['POST'])
def replicate_message():
    data = request.json
    message = data.get('message')
    print(f"Received message for replication: {message}")

    # Simulating delay
    time.sleep(2)

    replicated_messages.append(message)
    return jsonify({"status": "Message received"}), 200


@app.route('/messages', methods=['GET'])
def get_replicated_messages():
    return jsonify({"replicated_messages": replicated_messages})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
