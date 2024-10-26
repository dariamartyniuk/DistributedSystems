```markdown
# Message Replication Service

This application provides a master-secondary architecture for message replication using a configurable write concern parameter. The service allows for asynchronous messaging and guarantees that messages are replicated to a specified number of secondary servers before confirming receipt to the client.

## Features

- **Master-Secondary Replication**: Messages are sent from the master server to multiple secondary servers.
- **Write Concern Parameter**: Configurable `w` parameter allows clients to specify how many acknowledgments to wait for from secondary servers before confirming receipt.
- **Asynchronous Processing**: The application processes replication requests asynchronously for improved performance.
- **Error Handling**: Provides feedback on the success or failure of message replication.

## Architecture

- **Master Server**: Receives messages and manages the replication process.
- **Secondary Servers**: Replicate the received messages. The number of required acknowledgments can be configured through the `w` parameter.

## Endpoints

### 1. Send Message

- **URL**: `/send`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
      "message": "Your message here",
      "w": 1 // Optional, default is 1
  }
  ```
- **Response**:
  - **Success**: 
    ```json
    {
        "acks_received": <number>,
        "status": "Message replicated successfully"
    }
    ```
  - **Failure**:
    ```json
    {
        "acks_received": <number>,
        "status": "Not enough acks received"
    }
    ```
- **Description**: Sends a message to the master server, which then replicates it to the secondary servers. The server will respond as soon as it has received the required number of acknowledgments specified by the `w` parameter.

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose

### Installation Steps

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. Build and run the application using Docker Compose:
   ```bash
   docker-compose up --build
   ```

3. The master server will be running at `http://localhost:5000`.

## Testing the Application

You can test the application using `curl` or any API testing tool like Postman. Here are some example requests:

### Send a Message with `w=1`:
```bash
curl -X POST http://localhost:5000/send -H "Content-Type: application/json" -d '{"message": "Hello, World with w=1", "w": 1}'
```

### Send a Message with `w=3`:
```bash
curl -X POST http://localhost:5000/send -H "Content-Type: application/json" -d '{"message": "Hello, World with w=3", "w": 3}'
```

## Notes

- If `w=1`, the application will respond as soon as it receives acknowledgment from the master.
- If `w>1`, the application will wait until the specified number of acknowledgments is received from the secondary servers.
- The application is designed to handle various write concern levels, allowing flexibility in message replication.
