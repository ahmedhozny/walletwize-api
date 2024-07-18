import socketio
import json

# Create a Socket.IO client
sio = socketio.Client()


@sio.event
def connect():
    print("Connection established")


@sio.event
def disconnect():
    print("Disconnected from server")


@sio.event
def response(data):
    print(f"Received message: {data}")


def send_sync_data():
    client_id = "your_client_id"

    # Sample sync data
    payload = {
        "data": {
            "id": 1,
            "name": "John Doe",
            "DOB": "1990-01-01"
        },
        "operation": "I",  # or 'U' for update, 'D' for delete
        "table_name": "client_table"
    }

    # Send sync data to the server
    sio.send(json.dumps(payload))


if __name__ == "__main__":
    sio.connect("http://localhost:5000")
    print("Sending...")
    send_sync_data()
    print("Sent")
    sio.wait()
