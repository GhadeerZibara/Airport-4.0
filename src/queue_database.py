import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
CONNECTION_STRING = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg2.connect(CONNECTION_STRING)


def create_tables():
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS queue_events (
            id          SERIAL PRIMARY KEY,
            timestamp   TIMESTAMP NOT NULL,
            track_id    INT NOT NULL,
            event_type  VARCHAR(50) NOT NULL,
            wait_time   FLOAT,
            zone        VARCHAR(50),
            session     VARCHAR(255)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS queue_snapshots (
            id                SERIAL PRIMARY KEY,
            timestamp         TIMESTAMP NOT NULL,
            queue_length      INT NOT NULL,
            average_wait_time FLOAT,
            longest_wait_time FLOAT,
            total_served      INT,
            zone              VARCHAR(50),
            session           VARCHAR(255)
        )
    """)

    conn.commit()
    conn.close()


def log_queue_event(track_id, event_type, wait_time=None, zone=None, session=None):
    """Inserts one entry or exit event into queue_events.

    Args:
        track_id:   ByteTrack's integer ID for the person.
        event_type: 'enter' or 'exit'.
        wait_time:  Seconds spent in zone — populated on exit events only.
        zone:       Name of the zone where the event occurred.
        session:    Source video filename, used to separate runs.
    """
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO queue_events (timestamp, track_id, event_type, wait_time, zone, session)
        VALUES (NOW(), %s, %s, %s, %s, %s)
    """, (int(track_id), event_type, wait_time, zone, session))

    conn.commit()
    conn.close()


def log_snapshot(queue_length, average_wait_time, longest_wait_time,
                 total_served, zone=None, session=None):
    """Inserts a periodic summary row into queue_snapshots.

    Called every 30 seconds per zone to build a timeline of queue state.
    """
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO queue_snapshots
            (timestamp, queue_length, average_wait_time, longest_wait_time,
             total_served, zone, session)
        VALUES (NOW(), %s, %s, %s, %s, %s, %s)
    """, (queue_length, average_wait_time, longest_wait_time,
          total_served, zone, session))

    conn.commit()
    conn.close()
