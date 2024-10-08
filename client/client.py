import socket

def start_echo_client(host='127.0.0.1', port=12345):
    # Create a TCP/IP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    client_socket.connect((host, port))

    try:
        # Send data
        message = input("Enter a message to send to the server: ")
        client_socket.sendall(message.encode())

        # Receive response from the server
        data = client_socket.recv(1024)
        print(f"Received echo: {data.decode()}")

    finally:
        # Close the connection
        client_socket.close()

if __name__ == "__main__":
    start_echo_client()
