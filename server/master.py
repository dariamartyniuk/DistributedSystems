from flask import Flask, request, jsonify
import asyncio
import aiohttp

app = Flask(__name__)

messages = []
secondary_servers = ["http://host.docker.internal:5001", "http://host.docker.internal:5002"]

async def replicate_message(session, server, message):
    try:
        async with session.post(f'{server}/replicate', json={"message": message}) as response:
            response.raise_for_status()
            print(f"Successfully replicated message to {server}")
    except aiohttp.ClientError as e:
        print(f"Error replicating message to {server}: {e}")
        return False
    return True

@app.route('/messages', methods=['POST'])
def add_message():
    data = request.json
    message = data.get('message')
    messages.append(message)

    async def replicate_to_all_servers(message):
        async with aiohttp.ClientSession() as session:
            tasks = [replicate_message(session, server, message) for server in secondary_servers]
            results = await asyncio.gather(*tasks)
            if not all(results):
                return False
        return True

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    success = loop.run_until_complete(replicate_to_all_servers(message))

    if not success:
        return jsonify({"error": "Replication failed for one or more servers"}), 500

    return jsonify({"status": "Message replicated"}), 200


@app.route('/messages', methods=['GET'])
def get_messages():
    return jsonify({"messages": messages})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
