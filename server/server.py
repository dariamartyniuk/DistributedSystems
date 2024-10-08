from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

messages = []
secondary_servers = ["http://secondary1:5001", "http://secondary2:5002"]

@app.route('/messages', methods=['POST'])
def add_message():
    data = request.json
    message = data.get('message')
    messages.append(message)

    # Replicate message to secondaries
    for server in secondary_servers:
        response = requests.post(f'{server}/replicate', json={"message": message})
        if response.status_code != 200:
            return jsonify({"error": "Replication failed"}), 500

    return jsonify({"status": "Message replicated"}), 200

@app.route('/messages', methods=['GET'])
def get_messages():
    return jsonify({"messages": messages})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
