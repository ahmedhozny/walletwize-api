import socketio
import json
from sqlalchemy import create_engine, select, MetaData, Table, func
from sqlalchemy.orm import sessionmaker
from app.models.backup_models import BaseModel, ChangeLog

# Define your engine and connect to your client-side database
engine = create_engine('sqlite:///walletwize.db')

# Create the change_log table if it doesn't exist
BaseModel.metadata.create_all(engine)

# Create triggers for specific tables
ChangeLog.create_triggers_for_sqlite_table(engine, 'sources')
ChangeLog.create_triggers_for_sqlite_table(engine, 'transactions')

# Create a Socket.IO client
sio = socketio.Client()

# Create a session to interact with the database
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# Replace 'your_token_here' with your actual token
auth_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhaG1ob3NueTIwMDJAZ21haWwuY29tIiwiaWF0IjoxNzIyMDIyMTgwLCJleHAiOjE3MjQ2MTQxODB9.-p9t3A2aveL1I8g23cDY7l3ulGrRCQ1GpF-CFislJEc'
@sio.event
def connect():
    print("Connection established")


@sio.event
def disconnect():
    print("Disconnected from server")


@sio.event
def response(data):
    print(f"Received message: {data}")


@sio.event
def save_data(data):
    print(f"Received message: {data}")


def send_sync_data():
    # Query the change_log for unsynced changes
    change_log_table = Table('change_log', MetaData(), autoload_with=engine)
    changes_query = select(change_log_table).where(change_log_table.c.sync_time.is_(None))
    changes = session.execute(changes_query).fetchall()

    for change in changes:
        table_name = change['table_name']
        row_id = change['row_id']
        operation = change['operation']

        # Fetch the actual data from the specified table based on row_id
        table = Table(table_name, MetaData(), autoload_with=engine)
        record_query = select(table).where(table.c.id == row_id)
        record = session.execute(record_query).fetchone()

        if record:
            payload = {
                "log_id": change['id'],
                "table_name": table_name,
                "operation": operation,
                "timestamp": change['change_time'].isoformat(),
                "data": dict(record)
            }

            # Send sync data to the server
            sio.emit('save_data', json.dumps(payload))

            # Update the sync_time in change_log
            update_query = change_log_table.update().where(change_log_table.c.id == change['id']).values(
                sync_time=func.now())
            session.execute(update_query)
            session.commit()


if __name__ == "__main__":
    sio.connect("http://16.170.98.54", headers={'Authorization': f'Bearer {auth_token}'})
    print("Sending...")
    send_sync_data()
    print("Sent")