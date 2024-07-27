import json
from datetime import datetime, timedelta

from flask import Flask, request, jsonify
from flask_pydantic import validate
from flask_socketio import SocketIO, emit, disconnect

import logging

from sqlalchemy.exc import NoResultFound

from app.accounts_databases.backup import Backup
from app.authentcation.basic_auth import BasicAuthentication
from app.schemas import AccountCreate, AccountCredentials
from app.exceptions import *
from app.storage import Storage

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

storage = Storage()
auth = BasicAuthentication(storage)

# app.config["DEBUG"] = True


@app.errorhandler(AppException)
def handle_app_exception(error):
    logger.exception(error)
    return 'Internal Server Error', 500


@app.errorhandler(UserException)
def handle_user_exception(error):
    response = {'error': error.message, **error.extra}
    return jsonify(response), error.status


@app.route('/')
def index():
    return {'message': 'API is up and running!'}


@app.route('/login', methods=['POST'])
@validate()
def login(body: AccountCredentials):
    user = auth.validate_user(body)
    token = auth.create_access_token(user, datetime.utcnow(), expires_delta=timedelta(days=30))
    storage.user_storage().add_token(user, token)
    return {"token": token, "token_type": "bearer"}


@app.route('/register', methods=['POST'])
@validate()
def register(body: AccountCreate):
    user = auth.register_user(body)
    Backup(user.account_uuid)
    return {"message": "Account successfully registered!"}


@app.route("/protected", methods=['GET'])
@validate()
def protected():
    authorization_header = request.headers.get('Authorization')
    if not authorization_header:
        return {'error': 'Missing Authorization header'}

    if len(authorization_header.split(" ")) != 2:
        return {'error': 'Invalid Authorization header'}
    auth.verify_access_token(authorization_header)
    return {'message': "Authorized"}


@app.route('/logout', methods=['POST'])
@validate()
def logout():
    authorization_header = request.headers.get('Authorization')
    print(authorization_header)
    if not authorization_header:
        return {'error': 'Missing Authorization header'}

    if len(authorization_header.split(" ")) != 2:
        return {'error': 'Invalid Authorization header'}

    revoked = auth.revoke_token(authorization_header)
    if not revoked:
        raise UserTokenInvalid

    return {"message": "User successfully logged out (token revoked)!"}


@socketio.on('connect')
def handle_connect():
    authorization_header = request.headers.get('Authorization')
    if not authorization_header:
        print('Missing Authorization header')
        disconnect()
    try:
        token_data = auth.verify_access_token(authorization_header)
        user_email = token_data["email"]
        print(f"Client connected with email: {user_email}")
    except Exception:
        disconnect()


@socketio.on('disconnect')
def handle_disconnect():
    authorization_header = request.headers.get('Authorization')
    if not authorization_header:
        print('Client disconnected: Unknown user')
        return
    try:
        token_data = auth.verify_access_token(authorization_header)
        user_email = token_data["email"]
        print(f"Client disconnected with email: {user_email}")
    except Exception:
        print('Client disconnected: Unknown user')


@socketio.on('save_data')
def handle_upload_data(data):
    print("Message Received : " + data)
    try:
        authorization_header = request.headers.get('Authorization')
        if not authorization_header:
            emit("save_data", '{error: Missing Authorization header}')
            return

        token_data = auth.verify_access_token(authorization_header)
        user_email = token_data["email"]

        payload = json.loads(data)

        if payload is None:
            emit("save_data", '{error: Invalid payload}')
            return

        try:
            user = storage.user_storage().find_user_by_email(user_email)
        except NoResultFound:
            emit("save_data", '{error: User does not exist}')
            return

        backup_instance = Backup(user.account_uuid)
        backup_instance.sync_database(payload)

        emit("save_data", '{message: OK}')

    except UserException as e:
        if isinstance(e, (UserTokenInvalid, UserTokenExpired)):
            disconnect()
        emit("save_data", '{error: ' + e.message + '}')
    except json.decoder.JSONDecodeError:
        emit("save_data", '{error: Invalid payload}')
    except Exception as e:
        print(f"Error in handle_upload_data: {e}")
        emit("save_data", '{error: ' + str(e) + '}')


@socketio.on('load_data')
def handle_load_data(data):
    print("Load Data Request Received: " + data)
    try:
        authorization_header = request.headers.get('Authorization')
        if not authorization_header:
            emit("load_data", {'error': 'Missing Authorization header'})
            return

        token_data = auth.verify_access_token(authorization_header)
        user_email = token_data["email"]

        payload = json.loads(data)
        offset_id = payload.get('offset_id')

        if offset_id is None:
            emit("load_data", {'error': 'Invalid offset_id'})
            return

        try:
            user = storage.user_storage().find_user_by_email(user_email)
        except NoResultFound:
            emit("load_data", {'error': "No record found for the given email"})
            return

        try:
            backup_instance = Backup(user.account_uuid)
            changes = backup_instance.load_data(offset_id)
            emit("load_data", changes)
        except NoResultFound:
            emit("load_data", {'error': "No more changes found."})

    except UserException as e:
        if isinstance(e, (UserTokenInvalid, UserTokenExpired)):
            disconnect()
        emit("load_data", {'error': e.message})
    except json.decoder.JSONDecodeError:
        emit("load_data", {'error': 'Invalid payload'})
    except Exception as e:
        print(f"Error in handle_load_data: {e}")
        emit("load_data", {'error': str(e)})


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
