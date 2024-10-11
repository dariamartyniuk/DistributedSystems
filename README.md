# Replicated Log Application

This application demonstrates a simple replicated log architecture consisting of one **Master** and multiple **Secondary** servers. The Master accepts messages and ensures they are replicated across all Secondary servers in a blocking manner, waiting for an acknowledgment (ACK) from each Secondary before completing the request.

## Features

- **Master** exposes:
  - `POST /messages` - Appends a message to the log and replicates it to all secondaries.
  - `GET /messages` - Returns all messages from the log.
  
- **Secondary** exposes:
  - `POST /replicate` - Receives messages from the master for replication.
  - `GET /messages` - Returns all replicated messages stored in-memory.

## Requirements

- Docker
- Python 3.7+
  
## Setup Instructions

### Step 1: Clone the repository

```bash
git clone https://github.com/dariamartyniuk/DistributedSystems.git
```

### Step 2: Build Docker Images

Build the Docker images for both the Master and Secondary servers.

```bash
# Build Master image
docker build -t master:latest -f Dockerfile .

# Build Secondary image
docker build -t replica:latest -f Dockerfile .
```

### Step 3: Create Docker Network

Create a Docker network so that the Master and Secondary containers can communicate.

```bash
docker network create log_network
```

### Step 4: Run Master and Secondary Containers

Run the containers for the Master and Secondary servers.

```bash
# Run the Master on port 5000
docker run -d --name master1 --network log_network -p 5000:5000 master:latest

# Run Secondary servers on port 5001 and 5002
docker run -d --name secondary1 --network log_network -p 5001:5001 replica:latest
docker run -d --name secondary2 --network log_network -p 5002:5002 replica:latest
```

### Step 5: Test the Application

Once the containers are running, you can interact with the application using `curl`, Postman, or your browser.

#### Add a Message (Replication Request)
To add a message and have it replicated to all secondary servers:
```bash
curl -X POST http://localhost:5000/messages -H "Content-Type: application/json" -d '{"message":"Hello from master"}'
```

#### Retrieve Messages from Master
To retrieve all messages stored on the master:
```bash
curl http://localhost:5000/messages
```

#### Retrieve Messages from Secondary
To retrieve replicated messages from a secondary server (e.g., `secondary1`):
```bash
curl http://localhost:5001/messages
```

### Step 6: Check Logs

You can check the logs of each container to monitor communication and ensure that replication is occurring:

```bash
# Master logs
docker logs master1

# Secondary logs (for secondary1 and secondary2)
docker logs secondary1
docker logs secondary2
```

### Step 7: Stop the Application

To stop and remove the running containers:
```bash
docker stop master1 secondary1 secondary2
docker rm master1 secondary1 secondary2
```

### Troubleshooting

- Ensure that the Master and Secondary servers are running on the same Docker network (`log_network`).
- Check Docker container logs if replication fails.
- Ensure that the appropriate ports (5000, 5001, etc.) are mapped and accessible.
