import socketio

# Standard Python
sio = socketio.Client()

@sio.event
def connect():
    print('Connection established')

@sio.event
def disconnect():
    print('Disconnected from server')

@sio.on('payload')
def handle_payload(data):
    print('Payload received:', data)

def main():
    sio.connect('http://localhost:5000')

    # Example of sending data
    sio.emit('save_data', '{"example_key": "example_value"}')

    # Wait for a while to ensure the message is sent
    sio.wait()

if __name__ == '__main__':
    main()
