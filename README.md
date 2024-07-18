# WalletWize API

## Overview

WalletWize API is a backend service designed to manage user accounts, handle data synchronization, and facilitate real-time communication between clients and the server. The API is built with Flask, Flask-SocketIO, and SQLAlchemy, ensuring robust and efficient handling of user data and synchronization processes.

## Features

- User Registration and Authentication
- JWT-based Access Tokens
- Real-time Data Synchronization using Socket.IO
- Data Upload and Download with Change Log Management

## Setup

### Prerequisites

Ensure you have the following installed:

- Python 3.10 or higher
- `pip` (Python package installer)

### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/ahmedhozny/walletwize-api.git
    cd walletwize-api
    ```

2. **Create and activate a virtual environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
    ```

3. **Install the required packages:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up the database:**

    Ensure the `data_storage/` directory is created:

    ```bash
    mkdir -p data_storage
    ```

5. **Run the application:**

    ```bash
    flask run
    ```

    Or, if using the Socket.IO server:

    ```bash
    python app/main.py
    ```

## API Endpoints

### Authentication and User Management

- **Register a new user:**

    ```http
    POST /register
    ```

    **Request Body:**

    ```json
    {
        "email": "user@example.com",
        "password": "userpassword"
    }
    ```

    **Response:**

    ```json
    {
        "message": "Account successfully registered!",
        "email": "user@example.com"
    }
    ```

- **Login:**

    ```http
    POST /login
    ```

    **Request Body:**

    ```json
    {
        "email": "user@example.com",
        "password": "userpassword"
    }
    ```

    **Response:**

    ```json
    {
        "access_token": "jwt_token",
        "token_type": "bearer"
    }
    ```

- **Protected Endpoint:**

    ```http
    GET /protected
    ```

    **Headers:**

    ```http
    Authorization: Bearer jwt_token
    ```

    **Response:**

    ```json
    {
        "message": "Authorized"
    }
    ```

- **Logout:**

    ```http
    DELETE /logout
    ```

    **Request Body:**

    ```json
    {
        "access_token": "jwt_token"
    }
    ```

    **Response:**

    ```json
    {
        "message": "User successfully logged out (token revoked)!"
    }
    ```

### Socket.IO Events

- **Connect:**

    On connecting, clients must provide an `Authorization` header with a valid JWT token. Unauthorized connections are immediately disconnected.

    ```javascript
    socket.emit('connect', { headers: { 'Authorization': 'Bearer jwt_token' } });
    ```

- **Disconnect:**

    The server will print "Client disconnected" upon a client disconnecting.

- **Save Data:**

    To upload and synchronize data:

    ```javascript
    socket.emit('save_data', JSON.stringify({
        "log_id": 1,
        "table_name": "example_table",
        "operation": "I",
        "data": { "id": 1, "value": "example" },
        "timestamp": "2024-07-18T12:34:56"
    }));
    ```

    **Response:**

    ```json
    {
        "message": "OK"
    }
    ```

- **Load Data:**

    To load data changes from a specific offset:

    ```javascript
    socket.emit('load_data', JSON.stringify({ "offset_id": 1 }));
    ```

    **Response:**

    ```javascript
    socket.on('payload', (changes) => {
        console.log(changes);
    });
    ```

## Logging and Error Handling

The application logs errors and significant events, helping with debugging and monitoring. Custom error handlers are defined for `AppException` and `UserException` to provide meaningful error messages.

## Contribution

Contributions to the WalletWize API are welcome. Please submit pull requests or issues to the repository.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
