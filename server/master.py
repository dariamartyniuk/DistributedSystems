from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

messages = []
secondary_servers = ["http://host.docker.internal:5001", "http://host.docker.internal:5002"]

@app.route('/messages', methods=['POST'])
def add_message():
    data = request.json
    message = data.get('message')
    messages.append(message)

    for server in secondary_servers:
        try:
            response = requests.post(f'{server}/replicate', json={"message": message})
            response.raise_for_status()  # This will raise an error for bad responses
            print(f"Successfully replicated message to {server}")
        except requests.exceptions.RequestException as e:
            print(f"Error replicating message to {server}: {e}")
            return jsonify({"error": f"Replication failed for {server}"}), 500

    return jsonify({"status": "Message replicated"}), 200


@app.route('/messages', methods=['GET'])
def get_messages():
    return jsonify({"messages": messages})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
