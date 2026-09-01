import time
import psycopg


DB_HOST = "postgres"
DB_NAME = "media"
DB_USER = "mediauser"
DB_PASSWORD = "devpassword"


def get_connection():
    return psycopg.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def process_media():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE media
                SET status = 'queued',
                    processing_started_at = NULL
                WHERE status = 'processing'
                AND processing_started_at < CURRENT_TIMESTAMP - INTERVAL '5 minutes'
                """
            )

            recovered = cursor.rowcount

            if recovered:
                print(f"Recovered {recovered} stale job(s)", flush=True)

            conn.commit()
            cursor.execute(
                """
                SELECT id, title
                FROM media
                WHERE status = 'queued'
                ORDER BY id
                LIMIT 1
                FOR UPDATE SKIP LOCKED
                """
            )

            row = cursor.fetchone()

            if row is None:
                return False

            media_id, title = row

            print(f"Found media {media_id}: {title}, waiting before claiming...", flush=True)
            time.sleep(3)

            cursor.execute(
                """
                UPDATE media
                SET status = 'processing',
                    processing_started_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """,
                (media_id,),
            )

            print(f"Processing media {media_id}: {title}", flush=True)

        conn.commit()

    time.sleep(5)

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE media
                SET status = 'ready',
                    processing_started_at = NULL
                WHERE id = %s
                """,
                (media_id,),
            )

        conn.commit()

    print(f"Finished media {media_id}: {title}", flush=True)
    return True


while True:
    process_media()
    time.sleep(2)

