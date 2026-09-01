import json
import os
import socket
from http.server import BaseHTTPRequestHandler, HTTPServer

import psycopg


def get_db_connection():
    return psycopg.connect(
        host=os.environ["DB_HOST"],
        port=os.environ["DB_PORT"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        dbname=os.environ["DB_NAME"],
    )


class Handler(BaseHTTPRequestHandler):

    def send_json(self, status, data):
        body = json.dumps(data).encode()

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        hostname = socket.gethostname()

        if self.path == "/health":
            self.send_json(200, {"status": "healthy"})
            return

        if self.path == "/":
            self.send_json(
                200,
                {
                    "service": "media-api",
                    "pod": hostname,
                },
            )
            return

        if self.path == "/media":
            try:
                with get_db_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(
                            """
                            SELECT id, title, file_path, media_type, status, created_at
                            FROM media
                            ORDER BY id
                            """
                        )

                        rows = cursor.fetchall()

                media = []

                for row in rows:
                    media.append(
                        {
                            "id": row[0],
                            "title": row[1],
                            "file_path": row[2],
                            "media_type": row[3],
                            "status": row[4],
                            "created_at": row[5].isoformat(),
                        }
                    )

                self.send_json(200, media)

            except Exception as e:
                self.send_json(500, {"error": str(e)})

            return

        if self.path.startswith("/media/"):
            try:
                media_id = int(self.path.split("/")[-1])

                with get_db_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(
                            """
                            SELECT id, title, file_path, media_type, status, created_at
                            FROM media
                            WHERE id = %s
                            """,
                            (media_id,),
                        )

                        row = cursor.fetchone()

                if row is None:
                    self.send_json(404, {"error": "Media not found"})
                    return

                self.send_json(
                    200,
                    {
                        "id": row[0],
                        "title": row[1],
                        "file_path": row[2],
                        "media_type": row[3],
                        "status": row[4],
                        "created_at": row[5].isoformat(),
                    },
                )

            except ValueError:
                self.send_json(400, {"error": "Invalid media ID"})
            except Exception as e:
                self.send_json(500, {"error": str(e)})

            return

        self.send_json(404, {"error": "Not Found"})

    def do_POST(self):
        if self.path != "/media":
            self.send_json(404, {"error": "Not Found"})
            return

        try:
            content_length = int(self.headers["Content-Length"])
            body = self.rfile.read(content_length)
            data = json.loads(body)

            title = data["title"]
            file_path = data["file_path"]
            media_type = data["media_type"]

            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO media (title, file_path, media_type, status)
                        VALUES (%s, %s, %s, %s)
                        RETURNING id, title, file_path, media_type, status, created_at
                        """,
                        (title, file_path, media_type, "queued"),
                    )
                    row = cursor.fetchone()

            self.send_json(
                201,
                {
                    "id": row[0],
                    "title": row[1],
                    "file_path": row[2],
                    "media_type": row[3],
                    "status": row[4],
                    "created_at": row[5].isoformat(),
                },
            )

        except Exception as e:
            self.send_json(400, {"error": str(e)})

    def do_DELETE(self):
        if not self.path.startswith("/media/"):
            self.send_json(404, {"error": "Not Found"})
            return

        try:
            media_id = int(self.path.split("/")[-1])

            with get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        DELETE FROM media
                        WHERE id = %s
                        RETURNING id
                        """,
                        (media_id,),
                    )

                    row = cursor.fetchone()

            if row is None:
                self.send_json(404, {"error": "Media not found"})
                return

            self.send_json(
                200,
                {"message": "Media deleted", "id": row[0]},
            )

        except ValueError:
            self.send_json(400, {"error": "Invalid media ID"})
        except Exception as e:
            self.send_json(500, {"error": str(e)})


server = HTTPServer(("0.0.0.0", 8080), Handler)

print(f"API listening on port 8080 - {socket.gethostname()}")

server.serve_forever()
